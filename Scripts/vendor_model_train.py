import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# load dataset
df = pd.read_csv("D:/EM_38/data/vendors_features.csv")


# features
X = df[
[
"rating",
"listing_type",
"city",
"price_category",
"rating_category",
"description_length",
"is_metro_city",
"discount_percent"
]
]


# target
y = df["price"]


# categorical
cat_cols = ["listing_type","city","price_category","rating_category"]


# numerical
num_cols = ["rating","description_length","is_metro_city","discount_percent"]


# preprocessing
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


# pipeline
pipeline = Pipeline([
("preprocessor",preprocessor),
("model",model)
])


# train test split
X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=42)


# train
pipeline.fit(X_train,y_train)


# predictions
train_pred = pipeline.predict(X_train)
test_pred = pipeline.predict(X_test)


print("MAE:",mean_absolute_error(y_test,test_pred))
print("RMSE:",mean_squared_error(y_test,test_pred)**0.5)
print("Train R2:",r2_score(y_train,train_pred))
print("Test R2:",r2_score(y_test,test_pred))


# cross validation
kf = KFold(n_splits=5,shuffle=True,random_state=42)
cv = cross_val_score(pipeline,X,y,cv=kf,scoring="r2")

print("CV Scores:",cv)
print("CV Mean:",cv.mean())

print(df.groupby("listing_type")["price"].describe())
# save model
joblib.dump(pipeline,"D:/EM_38/models/vendor_price_model.pkl")

print("Vendor model saved")