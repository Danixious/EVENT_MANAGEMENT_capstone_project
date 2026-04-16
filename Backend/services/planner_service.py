from Backend.db_config import get_connection


# Fetch vendors from DB
def fetch_vendors_by_category(category, guests, location=None):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT 
            name,
            category,
            capacity,
            estimated_price,
            price_per_guest,
            rating,
            search_area
        FROM vendors
        WHERE category = %s
        AND capacity >= %s
    """

    params = [category, guests]

    # Optional location filter
    if location:
        query += " AND search_area ILIKE %s"
        params.append(f"%{location}%")

    query += " LIMIT 20;"

    cur.execute(query, params)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows


# Calculate cost based on category
def calculate_cost(vendor, category, guests):
    name, cat, capacity, estimated_price, price_per_guest, rating, location = vendor

    # Smart pricing logic
    if category == "caterer" and price_per_guest is not None:
        cost = price_per_guest * guests
        reason = f"Calculated using ₹{price_per_guest} per guest × {guests} guests"
    else:
        cost = estimated_price if estimated_price is not None else 0
        reason = "Using estimated price"

    return {
        "name": name,
        "category": cat,
        "capacity": capacity,
        "rating": rating,
        "location": location,  # actually search_area
        "cost": cost,
        "reason": reason
    }


#  Get top vendors for a category
def get_category_plan(category, guests, location=None):
    vendors = fetch_vendors_by_category(category, guests, location)

    results = []
    for vendor in vendors:
        processed = calculate_cost(vendor, category, guests)
        results.append(processed)

    # Sort by cost (cheapest first)
    results.sort(key=lambda x: x["cost"])

    return results[:5]  # Top 5 vendors


#  Generate full event plan
def generate_plan(guests, location=None):
    categories = ["venue", "caterer", "decorator", "photographer"]

    plan = {}

    for category in categories:
        plan[category] = get_category_plan(category, guests, location)

    return plan


#  TEST BLOCK
if __name__ == "__main__":
    plan = generate_plan(guests=150, location="Dehradun")

    print("\n🎯 GENERATED PLAN:\n")

    for category, vendors in plan.items():
        print(f"\n--- {category.upper()} ---")
        for v in vendors:
            print(v)