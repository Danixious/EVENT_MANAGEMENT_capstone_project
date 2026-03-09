from venue_model_train import pipeline, X_train, X_test, y_train, y_test
from sklearn.metrics import r2_score

train_predictions = pipeline.predict(X_train)
test_predictions = pipeline.predict(X_test)

train_r2 = r2_score(y_train, train_predictions)
test_r2 = r2_score(y_test, test_predictions)

print("Train R2:", train_r2)
print("Test R2:", test_r2)