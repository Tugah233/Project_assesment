# project_assessment
Overview
This project is designed to retrieve patient records from the medihealth_patients table, match them with data from the mis_patients table, and calculate match scores based on specific criteria such as mr_number, names, gender, birth date, and contact information. The matched records and their respective scores are written to a CSV file. 
The code connects to an Amazon Redshift database using environment variables to securely manage credentials and utilizes SQL queries to perform patient matching and scoring.


The rationale for scoring the matches between medihealth_patients and mis_patients as seen in the code is as follows;
1) mr_number and patient_id serves as a unique identifier for a patient hence the matching of both has a high percentage that the patients has been found thus the score 35.
2) first_name and pfirstname are usually not unique because a lot of people could have the same first name thus the score 10.
3) last_name and plast_name are also not very unique but a strong indicator thus the score 15.
4) gender is quite common as the patient is either a male or a female thus the score 5.
5) The birth date is a unique piece of information that can identify individuals, it's possible for multiple individuals to share the same birth date, the odds are relatively low compared to other fields like first or last names thus a score of 15.
6) Email addresses are unique to individuals and serve as a key identifier yet due to the possibility of shared family accounts or similar patterns and multiple accounts there's degree of uncertainty thus ths score 10.
7) Mobile numbers are unique to individuals, making them a reliable identifier for patient matching. Similar to email, there can be exceptions where family members might share a phone number or where individuals have multiple numbers. Thus, a score of 10.

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
