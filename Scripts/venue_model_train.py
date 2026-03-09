import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# load dataset
df = pd.read_csv("D:/EM_38/data/venues_features.csv")


# feature matrix
X = df[
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
]
]


# target
y = df["price"]


# categorical columns
cat_cols = ["venue_space_type","city","price_category","rating_category"]


# numerical columns
num_cols = ["rating","description_length","is_metro_city","discount_percent","listing_type_encoded"]


# preprocessing pipeline
preprocessor = ColumnTransformer(
[
("cat",OneHotEncoder(handle_unknown="ignore"),cat_cols),
("num","passthrough",num_cols)
]
)


# model
model = RandomForestRegressor(
n_estimators=200,
max_depth=10,
min_samples_split=5,
min_samples_leaf=2,
random_state=42
)


# full pipeline
pipeline = Pipeline([
("preprocessor",preprocessor),
("model",model)
])


# train test split
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=42)


# train model
pipeline.fit(X_train,y_train)


# predictions
pred = pipeline.predict(X_test)


# metrics
print("MAE:",mean_absolute_error(y_test,pred))
print("RMSE:",mean_squared_error(y_test,pred)**0.5)
print("R2:",r2_score(y_test,pred))


# save model
joblib.dump(pipeline,"D:/EM_38/models/venue_price_model.pkl")

print("Venue model saved")