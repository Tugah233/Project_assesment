# project_assessment
Overview
This project is designed to retrieve patient records from the medihealth_patients table, match them with data from the mis_patients table, and calculate match scores based on specific criteria such as names, gender, birth date, and contact information. The matched records and their respective scores are written to a CSV file.

The code connects to an Amazon Redshift database using environment variables to securely manage credentials and utilizes SQL queries to perform patient matching and scoring.

Features
Fetches all patient data from the medihealth_patients table.
Matches patients from the medihealth_patients table with mis_patients based on key identifiers.
Calculates individual and total match scores for each patient.
Exports the matched records and scores to a CSV file for easy reference.
Utilizes environment variables to secure sensitive database connection information.
Setup Instructions
Prerequisites
Python 3.x
PostgreSQL and psycopg2 library installed for database interaction.
Access to an Amazon Redshift cluster.
Required environment variables exported in your terminal.
