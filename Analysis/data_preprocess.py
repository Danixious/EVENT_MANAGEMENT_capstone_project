import pandas as pd
import numpy as np

# -----------------------------
# STEP 1: Load data
# -----------------------------
df = pd.read_csv("D:/EM_38/data/Venue_master.csv")

# -----------------------------
# STEP 2: Normalize column names
# -----------------------------
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# -----------------------------
# STEP 3: Normalize text columns
# -----------------------------
text_cols = ["listing_type", "venue_space_type", "city", "location"]

for col in text_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.lower().str.strip()

# -----------------------------
# STEP 4: Clean price columns
# -----------------------------
for col in ["price", "initial_price"]:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.strip()
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -----------------------------
# STEP 5: Rating cleanup
# -----------------------------
df["rating"] = pd.to_numeric(df["rating"], errors="coerce").clip(0, 5)

# -----------------------------
# STEP 6: ENTITY SEGREGATION (FINAL & CORRECT)
# -----------------------------
venues_df = df[df["listing_type"] == "banquet-halls"].copy()
vendors_df = df[df["listing_type"] != "banquet-halls"].copy()

# -----------------------------
# STEP 7: Drop irrelevant columns
# -----------------------------
vendors_df = vendors_df.drop(columns=["venue_space_type"], errors="ignore")

# -----------------------------
# STEP 8: Generate IDs
# -----------------------------
venues_df = venues_df.reset_index(drop=True)
vendors_df = vendors_df.reset_index(drop=True)

venues_df["venue_id"] = venues_df.index.map(lambda x: f"DLV_{x+1:06d}")
vendors_df["vendor_id"] = vendors_df.index.map(lambda x: f"VND_{x+1:06d}")

# -----------------------------
# STEP 9: Handle missing values
# -----------------------------
venues_df = venues_df.dropna(subset=["name"])
vendors_df = vendors_df.dropna(subset=["name"])

# Rating fill
venues_df["rating"] = venues_df["rating"].fillna(venues_df["rating"].median())
vendors_df["rating"] = vendors_df["rating"].fillna(vendors_df["rating"].median())

# Optional text fields
for col in ["description", "location", "city"]:
    if col in venues_df.columns:
        venues_df[col] = venues_df[col].fillna("")
    if col in vendors_df.columns:
        vendors_df[col] = vendors_df[col].fillna("")

# -----------------------------
# STEP 10: Final column ordering
# -----------------------------
venues_columns = [
    "venue_id", "name", "venue_space_type", "location", "city",
    "price", "initial_price", "rating", "description", "image_link"
]

vendors_columns = [
    "vendor_id", "name", "listing_type", "location", "city",
    "price", "initial_price", "rating", "description", "image_link"
]

venues_df = venues_df[venues_columns]
vendors_df = vendors_df[vendors_columns]

# -----------------------------
# STEP 11: Export
# -----------------------------
venues_df.to_csv("venues_db_ready.csv", index=False)
vendors_df.to_csv("vendors_db_ready.csv", index=False)

print("✅ Preprocessing fixed & completed")
print("Venues shape:", venues_df.shape)
print("Vendors shape:", vendors_df.shape)