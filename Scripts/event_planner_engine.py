import pandas as pd
import joblib
import random


# load trained models
venue_model = joblib.load("D:/EM_38/models/venue_price_model.pkl")
vendor_model = joblib.load("D:/EM_38/models/vendor_price_model.pkl")


# load feature datasets
venues = pd.read_csv("D:/EM_38/data/venues_features.csv")
vendors = pd.read_csv("D:/EM_38/data/vendors_features.csv")


# function to generate one plan
def generate_plan(city, budget):

    # filter venues by city
    venue_candidates = venues[venues["city"] == city].copy()

    if venue_candidates.empty:
        return None


    # predict venue prices
    venue_candidates["predicted_price"] = venue_model.predict(
        venue_candidates[
        [
        "rating",
        "venue_space_type",
        "city",
        "price_category",
        "rating_category",
        "description_length",
        "is_metro_city",
        "discount_percent",
        "listing_type_encoded"
        ]]
    )


    # compute venue score
    venue_candidates["score"] = (
        venue_candidates["rating"] * 2 -
        venue_candidates["predicted_price"] /
        venue_candidates["predicted_price"].max()
    )


    # sort venues by score
    venue_candidates = venue_candidates.sort_values("score", ascending=False)


    # select random venue from top venues
    venue = venue_candidates.head(8).sample(1).iloc[0]

    venue_cost = venue["predicted_price"]

    remaining_budget = budget - venue_cost


    # required vendor categories
    vendor_types = ["photographers", "decorators", "dj", "makeup-artists"]

    selected_vendors = []


    # select vendors for each category
    for vtype in vendor_types:

        vendor_candidates = vendors[
            (vendors["city"] == city) &
            (vendors["listing_type"] == vtype)
        ].copy()

        if vendor_candidates.empty:
            continue


        # predict vendor prices
        vendor_candidates["predicted_price"] = vendor_model.predict(
            vendor_candidates[
            [
            "rating",
            "listing_type",
            "city",
            "price_category",
            "rating_category",
            "description_length",
            "is_metro_city",
            "discount_percent"
            ]]
        )


        # compute vendor score
        vendor_candidates["score"] = (
            vendor_candidates["rating"] * 2 -
            vendor_candidates["predicted_price"] /
            vendor_candidates["predicted_price"].max()
        )


        # sort vendors by score
        vendor_candidates = vendor_candidates.sort_values("score", ascending=False)


        # pick random vendor from top options
        vendor = vendor_candidates.head(5).sample(1).iloc[0]

        vendor_cost = vendor["predicted_price"]


        # add vendor if budget allows
        if vendor_cost <= remaining_budget:

            selected_vendors.append(vendor)

            remaining_budget -= vendor_cost


    # calculate vendor cost
    total_vendor_cost = sum(v["predicted_price"] for v in selected_vendors)

    total_cost = venue_cost + total_vendor_cost


    return venue, selected_vendors, total_cost


# main planner
def plan_event(city, budget):

    print("\nGenerating Event Plans")
    print("----------------------------")
    print("City:", city)
    print("Budget:", budget)


    plans = []

    attempts = 0


    # generate 3 different plans
    while len(plans) < 3 and attempts < 20:

        plan = generate_plan(city, budget)

        attempts += 1

        if plan is not None:
            plans.append(plan)


    # display plans
    for i, (venue, vendors_list, total_cost) in enumerate(plans, start=1):

        print("\nEvent Plan", i)
        print("----------------------------")

        print("\nVenue:")
        print(venue["name"], "- ₹", round(venue["predicted_price"], 2))


        print("\nVendors:")

        if len(vendors_list) == 0:
            print("No vendors selected")

        else:
            for v in vendors_list:
                print(v["name"], "(", v["listing_type"], ")", "- ₹", round(v["predicted_price"], 2))


        print("\nTotal Estimated Cost:", round(total_cost, 2))
        print("Remaining Budget:", round(budget - total_cost, 2))


# run example
plan_event("delhi", 200000)