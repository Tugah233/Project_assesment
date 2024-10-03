import pandas as pd 

# create a simple Dataframe
data ={
    'life': ['Is not easy'],
    'success': ["Is a state of mind, don't be cuaght up in greed"],
    'Franklin Saint': ['We standing on business']
}

df = pd.DataFrame(data)

# Write the Dataframe to a CSV file
df.to_csv('Tugah.csv', index = False)

print("Now, Go Forth and Prosper")
