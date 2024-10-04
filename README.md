# Patient Data Matching Project

## Overview
This project is designed to retrieve patient records from the `medihealth_patients` table, match them with data from the `mis_patients` table, and calculate match scores based on specific criteria such as `mr_number`, names, gender, birth date, and contact information. The matched records and their respective scores are written to a CSV file.

The code connects to an Amazon Redshift database using credentials stored in an `.env` file to securely manage environment variables. SQL queries are used to perform patient matching and scoring.

## Scoring Rationale
The rationale for scoring the matches between `medihealth_patients` and `mis_patients` is as follows:

- **mr_number & patient_id**: These serve as unique identifiers for a patient. A match between them has a high likelihood of identifying the patient, hence the high score of **10**.
- **first_name & pfirstname**: First names are not unique, and many people can share the same first name. Therefore, it is scored **5**.
- **last_name & plast_name**: Last names, though not entirely unique, are a stronger identifier than first names. Hence, this is scored **7**.
- **gender**: Since gender is either male or female, it provides some information but is not a strong indicator, so it is scored **3**.
- **birth_date & dob**: While multiple individuals may share the same birth date, the odds are low, making this a strong identifier with a score of **7**.
- **email**: Email addresses are unique to individuals, but due to possible shared accounts, the score is **5**.
- **mobile**: Mobile numbers are usually unique, but exceptions such as shared family numbers or multiple numbers for one person exist, so it is scored **5**.
- **housetelephoneno & officetelephoneno**: Both are compared with the mobile number from the MediHealth data and scored **3** each.

## Features
- Fetches all patient data from the `medihealth_patients` table.
- Matches patients from the `medihealth_patients` table with `mis_patients` based on key identifiers.
- Calculates individual and total match scores for each patient.
- Exports the matched records and scores to a CSV file for easy reference.
- Utilizes environment variables stored in a `.env` file for securing sensitive database connection information.

## Setup Instructions

### Prerequisites
- Python 3.x
- PostgreSQL and the `psycopg2` library installed for database interaction.
- Access to an Amazon Redshift cluster.
- A `.env` file containing the necessary environment variables for the database connection.

### Code Usage
The core functionality is encapsulated in the `search_patient` function, which connects to the database, retrieves patient data, matches records, and writes the results to a CSV file.
