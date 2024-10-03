import pandas as pd

# Create a simple DataFrame
data = {
    'mr_number': ['nmc123', 'nmc421', 'nmc765'],
    'patient_name': ['Wevs', 'Tuagh', 'Finally'],
    'payment_method': ['cash', 'cash', 'insurance'],
    'Occupation': ['Engineer', 'Doctor', 'Teacher']
    }

df = pd.DataFrame(data)

# Write the DataFrame to a CSV file
df.to_csv('new_patients.csv', index=False)

print("CSV file saved as new_patients.csv")