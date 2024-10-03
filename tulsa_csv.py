import pandas as pd 
import lightgbm as lgb
import datetime

# Reading from the csv.file as a dataframe
store_df = pd.read_csv('/Users/samueln.y.fobi-berko/Downloads/revenue_csv.csv')

# Looking at the first five rows
store_df.head()

print(store_df.head())

# Looking at the shape of the last five rows
store_df.tail()

print(store_df.tail())