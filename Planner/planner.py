import pandas as pd
import numpy as np
import joblib

VENUE_TYPES = [
    "banquet hall",
    "hotel banquet hall",
    "party hall",
    "wedding lawn",
    "wedding resort"
]

# distance calculation
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = lat2.astype(float)
    lon2 = lon2.astype(float)

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


# filter vendors
def filter_vendors(df, user_lat, user_lon, guest_count, selected_categories):

    radius_list = [3, 5, 8, 10]
    filtered_vendors = {}

    for category in selected_categories:

        if category == "venue":
            category_df = df[
                (df["category"].str.strip().str.lower() == "venue") &
                (df["search_keyword"].str.strip().str.lower().isin(VENUE_TYPES))
            ].copy()
        else:
            category_df = df[
                df["search_keyword"].str.strip().str.lower() == category.lower()
            ].copy()

        if category_df.empty:
            filtered_vendors[category] = pd.DataFrame()
            continue

        found = False

        for radius in radius_list:

            category_df["distance"] = calculate_distance(
                user_lat, user_lon,
                category_df["latitude"], category_df["longitude"]
            )

            if category == "venue":
                temp_df = category_df[
                    (category_df["distance"] <= radius) &
                    (category_df["capacity"] >= guest_count)
                ]
            else:
                temp_df = category_df[
                    (category_df["distance"] <= radius)
                ]

            if not temp_df.empty:
                filtered_vendors[category] = temp_df
                found = True
                break

        if not found:
            category_df["distance"] = calculate_distance(
                user_lat, user_lon,
                category_df["latitude"], category_df["longitude"]
            )
            filtered_vendors[category] = category_df.nsmallest(5, "distance")

    return filtered_vendors


# load model
def load_model(model_path):
    return joblib.load(model_path)


# predict scores
def predict_scores(df, model):

    df = df.copy()

    df["base_price"] = df["base_price"].fillna(0)
    df["capacity"] = df["capacity"].replace(0, np.nan)

    df["price_per_guest"] = df["base_price"] / df["capacity"]
    df["price_per_guest"] = df["price_per_guest"].fillna(df["base_price"] * 0.1)
    df.loc[df["price_per_guest"] == 0, "price_per_guest"] = df["base_price"] * 0.1

    df["review_count"] = 50
    df["has_images"] = 1

    df["category_venue"] = (
        df["category"].str.strip().str.lower() == "venue"
    ).astype(int)

    areas = [
        "clement town", "dalanwala", "isbt area",
        "prem nagar", "rajpur road", "sahastradhara"
    ]

    for area in areas:
        df[f"search_area_{area}"] = (df["locality"].str.lower() == area).astype(int)

    feature_cols = [
        'rating', 'review_count', 'price_per_guest', 'capacity',
        'has_images', 'category_venue',
        'search_area_clement town', 'search_area_dalanwala',
        'search_area_isbt area', 'search_area_prem nagar',
        'search_area_rajpur road', 'search_area_sahastradhara'
    ]

    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0

    df["predicted_score"] = model.predict(df[feature_cols])

    return df


# improved realistic weight map
def allocate_budget(total_budget, selected_categories):

    weight_map = {
        "venue": 35,
        "caterer": 30,
        "event decorator": 15,
        "dj service": 10,
        "tent house": 5,
        "lighting service": 5,
        "wedding photographer": 5,
        "makeup artist": 3,
        "mehendi artist": 3,
        "wedding band": 4
    }

    weights = [weight_map.get(cat.lower(), 10) for cat in selected_categories]
    total_weight = sum(weights)

    return {
        cat: (w / total_weight) * total_budget
        for cat, w in zip(selected_categories, weights)
    }


# optimize vendors
def optimize_vendors(filtered_vendors, category_budgets, guest_count):

    optimized_vendors = {}

    for category, df in filtered_vendors.items():

        if df.empty:
            optimized_vendors[category] = df
            continue

        budget = float(category_budgets.get(category, 0))
        df = df.copy()

        df["cost"] = df["base_price"].fillna(0)

        df = df[df["cost"] <= budget]

        # smart fallback → cheapest options
        if df.empty:
            df = filtered_vendors[category].copy()
            df["cost"] = df["base_price"]
            df = df.nsmallest(3, "cost")

        df["affordability"] = (budget - df["cost"]) / budget if budget > 0 else 0
        df["affordability"] = df["affordability"].clip(lower=0)

        df["distance_score"] = 1 / (1 + df["distance"])
        df["area_priority"] = df["is_primary_area"].astype(int)

        score_df = df[df["predicted_score"] >= 0.5]
        if not score_df.empty:
            df = score_df

        df["final_score"] = (
            0.5 * df["predicted_score"] +
            0.25 * df["affordability"] +
            0.15 * df["distance_score"] +
            0.10 * (df["rating"] / 5) +
            0.30 * df["area_priority"]
        )

        df["budget_diff"] = abs(df["cost"] - budget)

        df = df.sort_values(by=["budget_diff", "final_score"], ascending=[True, False])
        optimized_vendors[category] = df.head(5)

    return optimized_vendors


# generate plans
def generate_plans(optimized_vendors, min_budget, max_budget):

    plans = {"budget_plan": {}, "balanced_plan": {}, "premium_plan": {}}

    for category, df in optimized_vendors.items():

        if df.empty:
            continue

        df_sorted = df.sort_values(by="cost")

        plans["budget_plan"][category] = df_sorted.iloc[0]

        balanced_df = df_sorted.iloc[1:] if len(df_sorted) > 1 else df_sorted
        balanced_df = balanced_df.copy()
        balanced_df["value_score"] = balanced_df["final_score"] / balanced_df["cost"]
        plans["balanced_plan"][category] = balanced_df.sort_values("value_score", ascending=False).iloc[0]

        premium_df = df.sort_values(by="cost", ascending=False).head(2)
        premium_df = premium_df.sort_values(by=["predicted_score", "rating"], ascending=False)
        plans["premium_plan"][category] = premium_df.iloc[0]

    return plans


# main planner
def run_event_planner(df, model, user_area, min_budget, max_budget, guest_count, selected_categories):

    user_lat = df["latitude"].mean()
    user_lon = df["longitude"].mean()

    df = predict_scores(df, model)

    selected_categories = list(set([
        "venue" if s in VENUE_TYPES else s
        for s in selected_categories
    ]))

    filtered_vendors = filter_vendors(
        df, user_lat, user_lon, guest_count, selected_categories
    )

    target_budget = (min_budget + max_budget) / 2
    category_budgets = allocate_budget(target_budget, selected_categories)

    optimized_vendors = optimize_vendors(
        filtered_vendors, category_budgets, guest_count
    )

    plans = generate_plans(optimized_vendors, min_budget, max_budget)

    return plans