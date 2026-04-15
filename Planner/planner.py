import pandas as pd
import numpy as np
import joblib


# calculate distance using haversine
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


# filter vendors per category with radius expansion
def filter_vendors(df, user_lat, user_lon, guest_count, selected_categories):

    radius_list = [3, 5, 8, 10]
    filtered_vendors = {}

    for category in selected_categories:

        category_df = df[df["search_keyword"].str.lower() == category.lower()].copy()
        found = False

        if category_df.empty:
            filtered_vendors[category] = pd.DataFrame()
            continue

        for radius in radius_list:

            category_df["distance"] = calculate_distance(
                user_lat, user_lon,
                category_df["latitude"], category_df["longitude"]
            )

            temp_df = category_df[
                (category_df["distance"] <= radius) &
                (category_df["capacity"] >= guest_count)
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


# load trained model
def load_model(model_path):
    return joblib.load(model_path)


# predict vendor scores
def predict_scores(df, model):

    df = df.copy()

    df["base_price"] = df["base_price"].fillna(0)
    df["capacity"] = df["capacity"].replace(0, np.nan)

    df["price_per_guest"] = df["base_price"] / df["capacity"]
    df["price_per_guest"] = df["price_per_guest"].fillna(df["base_price"] * 0.1)

    df.loc[df["price_per_guest"] == 0, "price_per_guest"] = df["base_price"] * 0.1

    df["review_count"] = 50
    df["has_images"] = 1

    df["category_venue"] = (df["service_type"].str.lower() == "venue").astype(int)

    areas = [
        "clement town",
        "dalanwala",
        "isbt area",
        "prem nagar",
        "rajpur road",
        "sahastradhara"
    ]

    for area in areas:
        col_name = f"search_area_{area}"
        df[col_name] = (df["locality"].str.lower() == area).astype(int)

    feature_cols = [
        'rating',
        'review_count',
        'price_per_guest',
        'capacity',
        'has_images',
        'category_venue',
        'search_area_clement town',
        'search_area_dalanwala',
        'search_area_isbt area',
        'search_area_prem nagar',
        'search_area_rajpur road',
        'search_area_sahastradhara'
    ]

    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0

    features = df[feature_cols]

    df["predicted_score"] = model.predict(features)

    return df


# allocate budget across categories
def allocate_budget(total_budget, selected_categories):

    weight_map = {
        "venue": 30,
        "hotel banquet hall": 30,
        "party hall": 30,
        "banquet hall": 30,
        "wedding resort": 30,
        "wedding lawn": 30,
        "caterer": 40,
        "tent house": 20,
        "event decorator": 15,
        "lighting service": 10,
        "wedding photographer": 10,
        "dj service": 10,
        "makeup artist": 5,
        "mehendi artist": 5,
        "wedding band": 5
    }

    weights = [weight_map.get(cat.lower(), 10) for cat in selected_categories]
    total_weight = sum(weights)

    category_budgets = {}

    for category, weight in zip(selected_categories, weights):
        category_budgets[category] = (weight / total_weight) * total_budget

    return category_budgets


# optimize vendor selection
def optimize_vendors(filtered_vendors, category_budgets, guest_count):

    optimized_vendors = {}

    for category, df in filtered_vendors.items():

        if df.empty:
            optimized_vendors[category] = df
            continue

        budget = float(category_budgets.get(category, 0))
        df = df.copy()

        # use base price as total cost
        df["cost"] = df["base_price"]

        # safety handling
        df["cost"] = df["cost"].fillna(0)
        df.loc[df["cost"] <= 0, "cost"] = df["base_price"]

        # soft budget filter
        filtered_df = df[df["cost"] <= budget]
        if not filtered_df.empty:
            df = filtered_df

        # affordability score
        if budget > 0:
            df["affordability"] = (budget - df["cost"]) / budget
        else:
            df["affordability"] = 0

        df["affordability"] = df["affordability"].clip(lower=0)

        # distance score
        df["distance_score"] = 1 / (1 + df["distance"])

        df["area_priority"] = df["is_primary_area"].astype(int)

        # soft score filter
        score_df = df[df["predicted_score"] >= 0.5]
        if not score_df.empty:
            df = score_df

        # final scoring
        df["final_score"] = (
        0.5 * df["predicted_score"] +
        0.25 * df["affordability"] +
        0.15 * df["distance_score"] +
        0.10 * (df["rating"] / 5) +
        0.30 * df["area_priority"]   # NEW
)

        df = df.sort_values(by="final_score", ascending=False)
        optimized_vendors[category] = df.head(5)
        print("DEBUG OPTIMIZED:", df[["name", "base_price", "cost"]].head())
    return optimized_vendors


# generate different plans
def generate_plans(optimized_vendors, min_budget, max_budget):

    plans = {
        "budget_plan": {},
        "balanced_plan": {},
        "premium_plan": {}
    }

    for category, df in optimized_vendors.items():

        if df.empty:
            continue

        df = df.copy()

        #BUDGET PLAN (cheapest)
        df_sorted_cost = df.sort_values(by="cost", ascending=True)
        plans["budget_plan"][category] = df_sorted_cost.iloc[0]

        #BALANCED PLAN (best value for money)
        # remove cheapest option to force diversity
        df_sorted_cost = df.sort_values(by="cost", ascending=True)

        if len(df_sorted_cost) > 1:
            df_balanced = df_sorted_cost.iloc[1:]  # skip cheapest
        else:
            df_balanced = df_sorted_cost

        df_balanced = df_balanced.copy()
        df_balanced["value_score"] = df_balanced["final_score"] / df_balanced["cost"]
        df_balanced = df_balanced.sort_values(by="value_score", ascending=False)

        plans["balanced_plan"][category] = df_balanced.iloc[0]

        #PREMIUM PLAN (high quality, ignore cheap bias)
        # take top 2 most expensive vendors
        df_sorted_expensive = df.sort_values(by="cost", ascending=False)

        if len(df_sorted_expensive) > 1:
            premium_df = df_sorted_expensive.iloc[:2]
        else:
            premium_df = df_sorted_expensive

        # pick best quality among expensive ones
        premium_df = premium_df.sort_values(
            by=["predicted_score", "rating"],
            ascending=False
        )

        plans["premium_plan"][category] = premium_df.iloc[0]

    return plans


# main planner function
def run_event_planner(df, model, user_area, min_budget, max_budget, guest_count, selected_categories):

    if user_area:
        area_df = df[df["locality"].str.lower() == user_area.lower()]
        if not area_df.empty:
            user_lat = area_df["latitude"].mean()
            user_lon = area_df["longitude"].mean()
        else:
            user_lat = df["latitude"].mean()
            user_lon = df["longitude"].mean()
    else:
        user_lat = df["latitude"].mean()
        user_lon = df["longitude"].mean()

    df = predict_scores(df, model)
    primary_df = df[df["is_primary_area"] == True]

    # threshold = minimum vendors needed
    if len(primary_df) >= len(selected_categories):
        df = primary_df

    filtered_vendors = filter_vendors(
        df, user_lat, user_lon, guest_count, selected_categories
    )

    category_budgets = allocate_budget(max_budget, selected_categories)

    optimized_vendors = optimize_vendors(
        filtered_vendors, category_budgets, guest_count
    )

    plans = generate_plans(optimized_vendors, min_budget, max_budget)

    print("FILTERED VENDORS:")
    for k, v in filtered_vendors.items():
        print(k, len(v))

    return plans