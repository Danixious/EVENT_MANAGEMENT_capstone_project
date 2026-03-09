import pandas as pd
import re


# clean price text
def clean_price(price):
    if pd.isna(price):
        return None
    price = str(price).replace("₹", "").replace(",", "")
    match = re.search(r"\d+", price)
    if match:
        return float(match.group())
    return None


# load raw dataset
df = pd.read_csv("D:/EM_38/data/Venue_master.csv", encoding="latin1")

print("Original shape:", df.shape)


# normalize column names
df.columns = df.columns.str.lower().str.strip()


# remove duplicates
df = df.drop_duplicates()


# clean text columns
text_cols = ["name","listing_type","location","city","description","venue_space_type"]

for col in text_cols:
    df[col] = df[col].astype(str).str.strip().str.lower()


# clean price columns
df["initial_price"] = df["initial_price"].apply(clean_price)
df["price"] = df["price"].apply(clean_price)


# convert ratings
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
df["rating"] = df["rating"].fillna(df["rating"].mean())


# drop rows without starting price
df = df.dropna(subset=["initial_price"])


# rename column
df = df.rename(columns={"initial_price":"starting_price"})


# split venues and vendors
venues = df[df["listing_type"]=="banquet-halls"].copy()
vendors = df[df["listing_type"]!="banquet-halls"].copy()


# scale venue prices only
venues["starting_price"] = venues["starting_price"] * 100
venues["price"] = venues["price"] * 100


# compute avg price
venues["avg_price"] = (venues["starting_price"] + venues["price"]) / 2
vendors["avg_price"] = (vendors["starting_price"] + vendors["price"]) / 2


# reset index
venues = venues.reset_index(drop=True)
vendors = vendors.reset_index(drop=True)


# create ids
venues.insert(0,"venue_id",["VEN_"+str(i).zfill(6) for i in range(len(venues))])
vendors.insert(0,"vendor_id",["VND_"+str(i).zfill(6) for i in range(len(vendors))])


# save clean datasets
venues.to_csv("D:/EM_38/data/venues_clean.csv",index=False)
vendors.to_csv("D:/EM_38/data/vendors_clean.csv",index=False)


print("Preprocessing completed")
print("Venues:",venues.shape)
print("Vendors:",vendors.shape)