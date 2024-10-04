import os
import csv
import psycopg2
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Fetch database credentials from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_SCHEMA = os.getenv('DB_SCHEMA')

# Function to search for a patient and write results to a CSV
def search_patient(fullname=None, mr_number=None, birth_date=None, mobile=None):
    conn = None
    try:
        conn = psycopg2.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT)

        # Create a cursor object
        cur = conn.cursor()

        # Set the schema
        cur.execute(f'SET search_path TO {DB_SCHEMA};')

        # Fetch all data from medihealth_patients table
        cur.execute("SELECT mr_number, first_name, last_name, gender, birth_date, mobile, email FROM medihealth__patients;")
        medihealth_patients = cur.fetchall()

        # Open a CSV file for writing results
        with open('matches.csv', mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write header row
            writer.writerow([
                "mr_number", "fullname", "gender", "birth_date", "mobile", "email", 
                "patient_id", "pfullname", "pgender", "pdob","housemobile", "officemobile", "pmobile", "pemail",
                "mr_number_score", "first_name_score", "last_name_score", "fullname_score", 
                "birth_date_score", "mobile_score", "housemobile_score", "officemobile_score", "email_score", "match_score"
            ])

            match_count = 0

            # Loop through each patient data and search for matches
            print("Processing patients...")

            for patient in medihealth_patients:
                mr_number, first_name, last_name, gender, birth_date, mobile, email = patient
                fullname = f"{first_name} {last_name}"

                # SQL query to search for matches based on patient data
                query = """
                    SELECT
                        mh.mr_number,
                        mh.first_name || ' ' || mh.last_name AS fullname,
                        mh.gender,
                        mh.birth_date,
                        mh.mobile,
                        mh.email,
                        mp.patient_id,
                        mp.pfirstname || ' ' || mp.plastname AS pfullname,
                        mp.gender AS pgender,
                        mp.dob AS pdob,
                        mp.housetelephoneno AS housemobile,
                        mp.officetelephoneno AS officemobile,
                        mp.mobile AS pmobile,
                        mp.email AS pemail,
                        CASE WHEN mh.mr_number = mp.patient_id THEN 10 ELSE 0 END AS mr_number_score,
                        CASE WHEN LOWER(mh.first_name) = LOWER(mp.pfirstname) THEN 7 ELSE 0 END AS first_name_score,
                        CASE WHEN LOWER(mh.last_name) = LOWER(mp.plastname) THEN 8 ELSE 0 END AS last_name_score,
                        CASE WHEN LOWER(mh.first_name || ' ' || mh.last_name) = LOWER(mp.pfirstname || ' ' || mp.plastname) THEN 10 ELSE 0 END AS fullname_score,
                        CASE WHEN mh.birth_date = mp.dob THEN 8 ELSE 0 END AS birth_date_score,
                        CASE WHEN mh.mobile = mp.mobile THEN 3 ELSE 0 END AS mobile_score,
                        CASE WHEN mh.mobile = mp.housetelephoneno THEN 3 ELSE 0 END AS housemobile_score,
                        CASE WHEN mh.mobile = mp.officetelephoneno THEN 3 ELSE 0 END AS officemobile_score,
                        CASE WHEN LOWER(mh.email) = LOWER(mp.email) THEN 7 ELSE 0 END AS email_score,
                        (
                            CASE WHEN mh.mr_number = mp.patient_id THEN 10 ELSE 0 END +
                            CASE WHEN LOWER(mh.first_name) = LOWER(mp.pfirstname) THEN 7 ELSE 0 END +
                            CASE WHEN LOWER(mh.last_name) = LOWER(mp.plastname) THEN 8 ELSE 0 END +
                            CASE WHEN LOWER(mh.first_name || ' ' || mh.last_name) = LOWER(mp.pfirstname || ' ' || mp.plastname) THEN 10 ELSE 0 END +
                            CASE WHEN mh.birth_date = mp.dob THEN 8 ELSE 0 END +
                            CASE WHEN mh.mobile = mp.mobile THEN 3 ELSE 0 END +
                            CASE WHEN mh.mobile = mp.housetelephoneno THEN 3 ELSE 0 END +
                            CASE WHEN mh.mobile = mp.officetelephoneno THEN 3 ELSE 0 END +
                            CASE WHEN LOWER(mh.email) = LOWER(mp.email) THEN 7 ELSE 0 END
                        ) AS match_score
                    FROM 
                        medihealth__patients mh
                    LEFT JOIN 
                        mis__patients mp
                    ON 
                        mh.mr_number = mp.patient_id
                        OR (
                            LOWER(mh.first_name) = LOWER(mp.pfirstname)
                            OR LOWER(mh.last_name) = LOWER(mp.plastname)
                            OR LOWER(mh.first_name || ' ' || mh.last_name) = LOWER(mp.pfirstname || ' ' || mp.plastname)
                            OR mh.birth_date = mp.dob
                            OR mh.mobile = mp.mobile
                            OR mh.mobile = mp.housetelephoneno
                            OR mh.mobile = mp.officetelephoneno
                            OR LOWER(mh.email) = LOWER(mp.email)
                        )
                    WHERE 
                        (%s IS NULL OR LOWER(mh.first_name || ' ' || mh.last_name) = LOWER(%s)) OR
                        (%s IS NULL OR mh.mr_number = %s) OR
                        (%s IS NULL OR mh.birth_date = %s) OR
                        (%s IS NULL OR mh.mobile = %s)
                    ORDER BY match_score DESC;
                """

                # Execute the SQL query with parameters from each patient
                cur.execute(query, (
                    fullname, fullname,
                    mr_number, mr_number,
                    birth_date, birth_date,
                    mobile, mobile
                ))

                # Fetch results and write them to the CSV file if match score > 0
                results = cur.fetchall()
                if results:
                    for row in results:
                        if row[19] > 0:
                            writer.writerow(row)
                            match_count += 1

            print(f"Processing complete. {match_count} matches found.")

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        # Ensure cursor and connection are closed if they were opened
        if conn:
            cur.close()
            conn.close()
            print("Database connection closed.")

# Function to handle user prompts and initiate the search
def run_search():
    # Prompt user for the parameter to search by
    search_param = input("What parameter would you like to search by (fullname, mr_number, birth_date, mobile)? ").strip().lower()

    # Prompt user for the value to search
    search_value = input(f"Enter the value for {search_param}: ").strip()

    # Run the search based on the chosen parameter
    if search_param == 'fullname':
        search_patient(fullname=search_value)
    elif search_param == 'mr_number':
        search_patient(mr_number=search_value)
    elif search_param == 'birth_date':
        search_patient(birth_date=search_value)
    elif search_param == 'mobile':
        search_patient(mobile=search_value)
    else:
        print("Invalid parameter. Please choose from fullname, mr_number, birth_date, or mobile.")

    # Output matches found
    print(f"Search for {search_param} = {search_value} completed.")


# Run the search function to handle user input and trigger the patient search
run_search()
