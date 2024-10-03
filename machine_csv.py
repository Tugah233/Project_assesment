import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np

# Load the CSV file
data = pd.read_csv('/Users/samueln.y.fobi-berko/Downloads/revenue_csv.csv')

# Convert reporting_date to datetime
data['reporting_date'] = pd.to_datetime(data['reporting_date'])

# Extract year and month from reporting_date
data['year'] = data['reporting_date'].dt.year
data['month'] = data['reporting_date'].dt.month

# Group data by year, month, site, payment_method, revenue_centre, and business_unit
# Sum the revenue (amount) for each group for monthly data
monthly_data = data.groupby(
    ['year', 'month', 'site', 'payment_method', 'revenue_centre', 'business_unit']
)['amount'].sum().reset_index()

# Prepare features (X) and target (y)
X = monthly_data[['year', 'month', 'site', 'payment_method', 'revenue_centre', 'business_unit']]
y = monthly_data['amount']

# One-hot encode categorical features
X = pd.get_dummies(X, columns=['site', 'payment_method', 'revenue_centre', 'business_unit'], drop_first=True)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# LightGBM dataset
train_data = lgb.Dataset(X_train, label=y_train)
test_data = lgb.Dataset(X_test, label=y_test)

# Set parameters for the model
params = {
    'objective': 'regression',
    'metric': 'rmse',
    'verbosity': -1,
}

# Train the LightGBM model
model = lgb.train(
    params,
    train_data,
    num_boost_round=1000
)

# Predict on the test set and calculate RMSE
y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f'RMSE: {rmse}')

# Generate predictions for the next month for all combinations
# Find the last available date in the dataset
last_year = monthly_data['year'].max()
last_month = monthly_data[monthly_data['year'] == last_year]['month'].max()

# Increment the month by 1
if last_month == 12:
    next_year = last_year + 1
    next_month = 1
else:
    next_year = last_year
    next_month = last_month + 1

# Get all unique combinations of 'site', 'payment_method', 'revenue_centre', 'business_unit'
unique_combinations = monthly_data[['site', 'payment_method', 'revenue_centre', 'business_unit']].drop_duplicates()

# Prepare the DataFrame for the next month
next_month_data = unique_combinations.copy()
next_month_data['year'] = next_year
next_month_data['month'] = next_month

# One-hot encode the next month data to match the training data
next_month_data_encoded = pd.get_dummies(next_month_data, columns=['site', 'payment_method', 'revenue_centre', 'business_unit'], drop_first=True)

# Ensure columns match between train and next month data
next_month_data_encoded = next_month_data_encoded.reindex(columns=X_train.columns, fill_value=0)

# Predict revenue for each combination
next_month_predictions = model.predict(next_month_data_encoded)

# Attach the predictions back to the original combinations
next_month_data['predicted_revenue'] = next_month_predictions

# Save the forecasted revenue for the next month to a CSV file
output_file = 'Predicted_revenue.csv'
next_month_data[['site', 'payment_method', 'revenue_centre', 'business_unit', 'predicted_revenue']].to_csv(output_file, index=False)

print(f'Saved predicted revenue to {output_file}')
