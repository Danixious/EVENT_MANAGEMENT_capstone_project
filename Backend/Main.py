import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Backend.db_config import get_connection
from Backend.queries import FETCH_VENDORS_QUERY
from Backend import queries
from Planner.planner import run_event_planner, load_model

# LOAD MODEL
MODEL_PATH = os.path.join("models", "vendor_recommendation_model.pkl")
model = load_model(MODEL_PATH)

#  Nearby Area Mapping
nearby_map = {
    "rajpur road": ["ballupur", "dalanwala", "clement town"],
    "ballupur": ["rajpur road", "isbt area"],
    "prem nagar": ["clement town", "dalanwala"],
    "isbt area": ["ballupur", "rajpur road"],
}

#  SERVICE NORMALIZATION
SERVICE_MAP = {
    "party hall": "banquet hall",
    "dj": "dj service",
    "decorator": "event decorator",
    "photographer": "wedding photographer"
}

def normalize_services(services):
    normalized = []

    for s in services:
        s = s.lower()

        if s == "party hall":
            normalized.extend(["party hall", "banquet hall", "hotel banquet hall"])
        elif s == "decorator":
            normalized.append("event decorator")
        elif s == "dj":
            normalized.append("dj service")
        else:
            normalized.append(s)

    return list(set(normalized))  # remove duplicates

#  FETCH FILTERED VENDORS
def get_filtered_vendors(locality, services, guest_count, month):

    conn = get_connection()
    if conn is None:
        raise Exception("❌ Database connection failed")

    cursor = conn.cursor()

    try:
        # Normalize inputs
        locality = locality.lower()
        services = [s.lower() for s in normalize_services(services)]

        # Include nearby areas
        locality_list = [locality]
        if locality in nearby_map:
            locality_list.extend(nearby_map[locality])

        # Execute query (IMPORTANT ORDER)
        cursor.execute(
            FETCH_VENDORS_QUERY,
            (
                guest_count,     # for dynamic pricing
                services,
                services,        # search_keyword
                locality_list,   # search_area
                200              # limit
            )
        )

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        df = pd.DataFrame(rows, columns=columns)

        df["category"] = df["category"].astype(str).str.strip().str.lower()
        df["search_keyword"] = df["search_keyword"].astype(str).str.strip().str.lower()

        VENUE_TYPES = ["banquet hall", "hotel banquet hall", "party hall", "wedding lawn", "wedding resort"]


        if df.empty:
            print("⚠️ No vendors found after filtering")
            return df

        #  DATA CLEANING
        numeric_cols = ["base_price", "capacity", "rating", "latitude", "longitude"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df["base_price"] = df["base_price"].fillna(10000)
        df["capacity"] = df["capacity"].fillna(guest_count)
        df["rating"] = df["rating"].fillna(3.5)

        # Planner required
        df["is_primary_area"] = df["locality"].str.lower() == locality

        # Debug logs
        print("\n Vendors fetched:", len(df))
        print(" Areas:", df["locality"].value_counts().to_dict())
        print("🛠 Services:", df["search_keyword"].value_counts().to_dict())

        return df

    except Exception as e:
        print(" Error in get_filtered_vendors:", e)
        return pd.DataFrame()

    finally:
        cursor.close()
        conn.close()


#  STORE EVENT
def store_event(user_id, event_type, event_date, guest_count, min_budget, max_budget):

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            queries.INSERT_EVENT_QUERY,
            (user_id, event_type, event_date, guest_count, min_budget, max_budget)
        )
        event_id = cursor.fetchone()[0]
        conn.commit()
        return event_id

    finally:
        cursor.close()
        conn.close()


#  STORE PLANS
def store_plans(event_id, plans):

    conn = get_connection()
    cursor = conn.cursor()

    stored_plans = []

    try:
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
        return stored_plans

    finally:
        cursor.close()
        conn.close()


#  MAIN PIPELINE
from datetime import datetime
def generate_event_plan(input_data):
    event_date_obj = datetime.strptime(input_data.event_date, "%Y-%m-%d")
    month = event_date_obj.month

    vendors_df = get_filtered_vendors(
        input_data.locality,
        input_data.services,
        input_data.guest_count,
        month
    )

    if vendors_df.empty:
        raise ValueError("❌ No vendors found in database")

    # Run planner
    raw_plans = run_event_planner(
        vendors_df,
        model,
        input_data.locality,
        input_data.min_budget,
        input_data.max_budget,
        input_data.guest_count,
        normalize_services(input_data.services)
    )

    # Format plans
    plans = format_plans(
        raw_plans,
        input_data.min_budget,
        input_data.max_budget
    )

    # Store event
    event_id = store_event(
        user_id=1,
        event_type=input_data.event_type,
        event_date=input_data.event_date,
        guest_count=input_data.guest_count,
        min_budget=input_data.min_budget,
        max_budget=input_data.max_budget
    )

    stored_plans = store_plans(event_id, plans)

    overall_status = "success"

    if any(p.get("status") == "adjusted_plan" for p in plans):
        overall_status = "adjusted_plan"

    return {
        "status": overall_status,
        "event_id": event_id,
        "plans": plans
}

#  FORMAT PLANS
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
                "vendor_id": str(row["vendor_id"]),
                "name": row["name"],
                "category": category,

                # Pricing
                "allocated_budget": float(cost),

                #  Score
                "score": float(row.get("final_score", 0)),

                #  Location info
                "address": row.get("address"),
                "location" : row.get("google_maps_url"),
                "latitude": float(row.get("latitude", 0)) if pd.notna(row.get("latitude")) else None,
                "longitude": float(row.get("longitude", 0)) if pd.notna(row.get("longitude")) else None,

                # Contact
                "contact": row.get("phone"),   # or phone / mobile (depends on DB column name)

                #  Website
                "website": row.get("website"),

                #  Rating
                "rating": float(row.get("rating", 0)) if pd.notna(row.get("rating")) else None
}

            total_cost += float(cost)
            vendors_list.append(vendor_data)
        remaining = max_budget - total_cost

        # budget check
        if total_cost > max_budget:
            status = "adjusted_plan"
            message = "⚠️ Budget too low. Showing closest possible plan."
            budget_gap = total_cost - max_budget
        else:
            status = "success"
            message = "Plan within budget."
            budget_gap = 0
        
        if total_cost < max_budget * 0.6:
            message = "⚠️ Budget exceeds available vendor pricing. Showing best possible plan."

        formatted.append({
            "plan_type": plan_type.replace("_plan", ""),
            "vendors": vendors_list,
            "total_cost": total_cost,
            "remaining_budget": max(0, remaining),
            "budget_gap": budget_gap,
            "status": status,
            "message": message,
            "optimization_score": 0
        })

    return formatted