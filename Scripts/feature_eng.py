import pandas as pd
from sklearn.preprocessing import LabelEncoder


# load cleaned datasets
venues = pd.read_csv("D:/EM_38/data/venues_clean.csv")
vendors = pd.read_csv("D:/EM_38/data/vendors_clean.csv")


# fill missing prices
venues["price"] = venues["price"].fillna(venues["avg_price"])
vendors["price"] = vendors["price"].fillna(vendors["avg_price"])


# create discount percent
def add_discount(df):
    df["discount_percent"] = ((df["starting_price"]-df["price"])/df["starting_price"])*100
    df["discount_percent"] = df["discount_percent"].fillna(0)
    return df


venues = add_discount(venues)
vendors = add_discount(vendors)


# price category
def price_category(p):
    if p < 50000:
        return "Budget"
    elif p < 150000:
        return "Mid"
    else:
        return "Premium"


venues["price_category"] = venues["price"].apply(price_category)
vendors["price_category"] = vendors["price"].apply(price_category)


# rating category
def rating_category(r):
    if r >= 4.5:
        return "Excellent"
    elif r >= 4.0:
        return "Good"
    elif r >= 3.5:
        return "Average"
    else:
        return "Low"


venues["rating_category"] = venues["rating"].apply(rating_category)
vendors["rating_category"] = vendors["rating"].apply(rating_category)


# description length
venues["description_length"] = venues["description"].astype(str).apply(len)
vendors["description_length"] = vendors["description"].astype(str).apply(len)


# metro city flag
metros = ["delhi","mumbai","bangalore","kolkata","chennai","hyderabad"]

venues["is_metro_city"] = venues["city"].apply(lambda x:1 if x in metros else 0)
vendors["is_metro_city"] = vendors["city"].apply(lambda x:1 if x in metros else 0)


# encode listing type
le = LabelEncoder()

venues["listing_type_encoded"] = le.fit_transform(venues["listing_type"])
vendors["listing_type_encoded"] = le.fit_transform(vendors["listing_type"])


# save features
venues.to_csv("D:/EM_38/data/venues_features.csv",index=False)
vendors.to_csv("D:/EM_38/data/vendors_features.csv",index=False)


print("Feature engineering completed")