import requests
import pandas as pd
import time

API_KEY = "AIzaSyCvyzjlmHmvIrr1SlN_AZ8tSk5EeUCgAHU"

# Vendor service categories
vendor_keywords = [
    "caterer",
    "wedding photographer",
    "event decorator",
    "dj service",
    "makeup artist",
    "event planner",
    "tent house",
    "lighting service",
    "florist",
    "mehendi artist",
    "wedding band"
]

# Venue categories
venue_keywords = [
    "banquet hall",
    "wedding lawn",
    "party hall",
    "wedding resort",
    "hotel banquet hall"
]

# Dehradun search zones
locations = [
    {"name":"Rajpur Road","lat":30.3256,"lng":78.0421},
    {"name":"Ballupur","lat":30.3165,"lng":78.0322},
    {"name":"Clement Town","lat":30.2834,"lng":77.9983},
    {"name":"Prem Nagar","lat":30.3511,"lng":77.9997},
    {"name":"Sahastradhara","lat":30.3872,"lng":78.1312},
    {"name":"Dalanwala","lat":30.3161,"lng":78.0500},
    {"name":"ISBT Area","lat":30.2880,"lng":78.0060}
]

RADIUS = 4000

def search_places(keyword, lat, lng):

    url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={RADIUS}&keyword={keyword}&key={API_KEY}"
    all_results = []

    while url:

        response = requests.get(url)
        data = response.json()

        for place in data.get("results", []):

            location = place.get("geometry", {}).get("location", {})

            photo_reference = None
            photo_url = None

            if "photos" in place:
                photo_reference = place["photos"][0].get("photo_reference")

                if photo_reference:
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_reference}&key={API_KEY}"

            all_results.append({
                "place_id": place.get("place_id"),
                "name": place.get("name"),
                "rating": place.get("rating"),
                "review_count": place.get("user_ratings_total"),
                "price_level": place.get("price_level"),
                "business_status": place.get("business_status"),
                "open_now": place.get("opening_hours",{}).get("open_now"),
                "address": place.get("vicinity"),
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
                "types": ",".join(place.get("types",[])),
                "photo_reference": photo_reference,
                "photo_url": photo_url
            })

        next_page = data.get("next_page_token")

        if next_page:
            time.sleep(2)
            url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken={next_page}&key={API_KEY}"
        else:
            url = None

    return all_results


all_places = []

# Collect vendors
for loc in locations:
    for keyword in vendor_keywords:

        print("Searching:", keyword, "in", loc["name"])

        results = search_places(keyword, loc["lat"], loc["lng"])

        for r in results:
            r["category"] = "vendor"
            r["search_keyword"] = keyword
            r["search_area"] = loc["name"]

        all_places.extend(results)


# Collect venues
for loc in locations:
    for keyword in venue_keywords:

        print("Searching:", keyword, "in", loc["name"])

        results = search_places(keyword, loc["lat"], loc["lng"])

        for r in results:
            r["category"] = "venue"
            r["search_keyword"] = keyword
            r["search_area"] = loc["name"]

        all_places.extend(results)


df = pd.DataFrame(all_places)

# Remove duplicates
df = df.drop_duplicates(subset="place_id")

df.to_csv("D:/EM_38/data/dehradun_event_marketplace_raw.csv",index=False)

print("Finished")
print("Total businesses collected:",len(df))