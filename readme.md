# EVENT_MANAGEMENT_capstone_project


venues.to_csv("D:/EM_38/data/venues_features.csv", index=False)
vendors.to_csv("D:/EM_38/data/vendors_features.csv", index=False)


venues = pd.read_csv("D:/EM_38/data/venues_clean.csv")
vendors = pd.read_csv("D:/EM_38/data/vendors_clean.csv")



PS D:\EM_38\Scripts> python vendor_model_train.py

Model Performance
---------------------
MAE: 24210.648681967163
RMSE: 37467.7680641669
MSE: 1403833643.7102048
Train R2: 0.7541072450249776
Test R2: 0.6120504646297298

Cross Validation R2 Scores: [0.60307013 0.58913991 0.5454254  0.71644915 0.47470744]
Average CV R2: 0.5857584049180062

Model saved to models/vendor_price_model.pkl


PS D:\EM_38\Scripts> python venue_model_train.py 
Model Performance
MAE: 19133.022859366465
RMSE: 25764.137654394657
MSE: 663790789.0745966
R2: 0.7955025500179495
Model saved to models/venue_price_model.pkl

PS D:\EM_38\Scripts> python event_planner_engine.py

Generating Smart Event Plan
----------------------------
City: delhi
Budget: 200000

Event Plan
----------------------------

Venue:
venizia sarovar portico - ₹ 92729.82

Vendors:

Total Estimated Cost: 92729.82
Remaining Budget: 107270.18