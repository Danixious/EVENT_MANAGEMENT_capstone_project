import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Backend.db_config import get_connection
from Backend import queries
import pandas as pd
from Planner.planner import run_event_planner,load_model

model = load_model("D:/EM_38/models/vendor_recommendation_model.pkl")
nearby_map = {
    "rajpur road": ["ballupur", "dalanwala", "clement town"],
    "ballupur": ["rajpur road", "isbt area"],
    "prem nagar": ["clement town", "dalanwala"],
    "isbt area": ["ballupur", "rajpur road"],
}
def get_filtered_vendors(locality, services, guest_count, month):

    conn = get_connection()
    cursor = conn.cursor()

    base_area = locality.lower()

    nearby_areas = nearby_map.get(base_area, [])

    all_areas = [base_area] + nearby_areas

    values = (
        services,
        all_areas,
        guest_count,
        200
)

    cursor.execute(queries.FETCH_VENDORS_QUERY, values)
    rows = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=columns)
    base_area = locality.lower()
    df["is_primary_area"] = df["locality"].str.lower() == base_area
    # convert numeric columns to float
    numeric_cols = ["base_price", "min_capacity", "max_capacity", "rating", "latitude", "longitude", "capacity"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    cursor.close()
    conn.close()

    return df


def store_event(user_id, event_type, event_date, guest_count, min_budget, max_budget):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        queries.INSERT_EVENT_QUERY,
        (user_id, event_type, event_date, guest_count, min_budget, max_budget)
    )

    event_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    return event_id


def store_plans(event_id, plans):
    conn = get_connection()
    cursor = conn.cursor()

    stored_plans = []

    for plan in plans:
        cursor.execute(
            queries.INSERT_PLAN_QUERY,
            (
                event_id,
                plan["plan_type"],
                plan["total_cost"],
                plan.get("remaining_budget", 0),
                plan.get("optimization_score", 0)
            )
        )

        plan_id = cursor.fetchone()[0]

        for vendor in plan["vendors"]:
            cursor.execute(
                queries.INSERT_PLAN_DETAILS_QUERY,
                (
                    plan_id,
                    vendor["vendor_id"],
                    vendor["allocated_budget"],
                    vendor.get("score", 0)
                )
            )

        stored_plans.append({
            "plan_id": plan_id,
            "plan_type": plan["plan_type"],
            "total_cost": plan["total_cost"]
        })

    conn.commit()
    cursor.close()
    conn.close()
    return stored_plans


def generate_event_plan(input_data):

    vendors_df = get_filtered_vendors(
        input_data["locality"],
        input_data["services"],
        input_data["guest_count"],
        input_data["month"]
    )
    print(vendors_df[["search_keyword", "capacity"]].head())
    if vendors_df.empty:
        raise ValueError("No vendors found in database")

    raw_plans = run_event_planner(
    vendors_df,
    model,
    input_data["locality"],
    input_data["min_budget"],
    input_data["max_budget"],
    input_data["guest_count"],
    input_data["services"]
)

    plans = format_plans(
        raw_plans,
        input_data["min_budget"],
        input_data["max_budget"]
    )
    print_clean_plans(raw_plans)
    event_id = store_event(
        user_id=1,
        event_type=input_data["event_type"],
        event_date=input_data["event_date"],
        guest_count=input_data["guest_count"],
        min_budget=input_data["min_budget"],
        max_budget=input_data["max_budget"]
    )

    stored_plans = store_plans(event_id, plans)
    return {
    "event_id": event_id,
    "plans": [
        {
            "plan_type": p["plan_type"],
            "total_cost": p["total_cost"]
        }
        for p in stored_plans
    ]
}
    print("VENDORS DF SHAPE:", vendors_df.shape)
    print(vendors_df["search_keyword"].value_counts())



def print_clean_plans(plans):
    print("\n--- FINAL PLANS ---")

    for plan_type, categories in plans.items():
        print(f"\n{plan_type.upper()}")

        total_cost = 0

        for category, row in categories.items():
            name = row["name"]
            cost = round(row["cost"], 2)

            print(f"{category} -> {name} (₹{cost})")
            total_cost += cost

        print("Total Cost:", round(total_cost, 2))


def format_plans(plans, min_budget, max_budget):

    formatted = []

    for plan_type, vendors_dict in plans.items():

        vendors_list = []
        total_cost = 0

        for category, row in vendors_dict.items():

            cost = row.get("cost", 0)
            if pd.isna(cost):
                cost = 0

            vendor_data = {
                "vendor_id": int(row["vendor_id"]),
                "name": row["name"],
                "category": category,
                "allocated_budget": float(cost),
                "score": float(row.get("final_score", 0))
            }

            total_cost += float(cost)
            vendors_list.append(vendor_data)
    
        formatted.append({
            "plan_type": plan_type,
            "vendors": vendors_list,
            "total_cost": total_cost,
            "remaining_budget": max_budget - total_cost,
            "optimization_score": 0
        })
    return formatted

# TEST RUN
if __name__ == "__main__":
    input_data = {
    "event_type": "birthday",
    "event_date": "2026-06-15",
    "locality": "rajpur road",
    "guest_count": 50,
    "min_budget": 80000,
    "max_budget": 90000,
    "services": ["party hall","caterer", "event decorator", "dj service"],
    "month": 6
}
    result = generate_event_plan(input_data)

    print(result)