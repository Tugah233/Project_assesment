import os
import csv
import psycopg2


# Fetch database credentials from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_SCHEMA = os.getenv('DB_SCHEMA')

# Function to search for a patient and write results to a CSV
def search_patient():
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
        with open('patient_search_results.csv', mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write header row
            writer.writerow([
                "mr_number", "first_name", "last_name", "gender", "birth_date", "mobile", "email", 
                "patient_id", "pfirst_name", "plast_name", "pgender", "pdob", "pmobile", "pemail",
                "mr_number_score", "first_name_score", "last_name_score", "gender_score", 
                "birth_date_score", "mobile_score", "email_score", "match_score"
            ])

            # Loop through each patient data and search for matches
            for patient in medihealth_patients:
                mr_number, first_name, last_name, gender, birth_date, mobile, email = patient

                # SQL query to search for matches based on patient data
                query = """
                    SELECT
                        mh.mr_number,
                        mh.first_name,
                        mh.last_name,
                        mh.gender,
                        mh.birth_date,
                        mh.mobile,
                        mh.email,
                        mp.patient_id,
                        mp.pfirstname AS pfirst_name,
                        mp.plastname AS plast_name,
                        mp.gender AS pgender,
                        mp.dob AS pdob,
                        mp.mobile AS pmobile,
                        mp.email AS pemail,
                        CASE WHEN mh.mr_number = mp.patient_id THEN 35 ELSE 0 END AS mr_number_score,
                        CASE WHEN LOWER(mh.first_name) = LOWER(mp.pfirstname) THEN 10 ELSE 0 END AS first_name_score,
                        CASE WHEN LOWER(mh.last_name) = LOWER(mp.plastname) THEN 15 ELSE 0 END AS last_name_score,
                        CASE WHEN LOWER(mh.gender) = LOWER(mp.gender) THEN 5 ELSE 0 END AS gender_score,
                        CASE WHEN mh.birth_date = mp.dob THEN 15 ELSE 0 END AS birth_date_score,
                        CASE WHEN mh.mobile = mp.mobile THEN 10 ELSE 0 END AS mobile_score,
                        CASE WHEN LOWER(mh.email) = LOWER(mp.email) THEN 10 ELSE 0 END AS email_score,
                        (
                            CASE WHEN mh.mr_number = mp.patient_id THEN 35 ELSE 0 END +
                            CASE WHEN LOWER(mh.first_name) = LOWER(mp.pfirstname) THEN 10 ELSE 0 END +
                            CASE WHEN LOWER(mh.last_name) = LOWER(mp.plastname) THEN 15 ELSE 0 END +
                            CASE WHEN LOWER(mh.gender) = LOWER(mp.gender) THEN 5 ELSE 0 END +
                            CASE WHEN mh.birth_date = mp.dob THEN 15 ELSE 0 END +
                            CASE WHEN mh.mobile = mp.mobile THEN 10 ELSE 0 END +
                            CASE WHEN LOWER(mh.email) = LOWER(mp.email) THEN 10 ELSE 0 END
                        ) AS match_score
                    FROM 
                        medihealth__patients mh
                    LEFT JOIN 
                        mis__patients mp
                    ON 
                        mh.mr_number = mp.patient_id
                        OR (
                            LOWER(mh.first_name) = LOWER(mp.pfirstname)
                            AND LOWER(mh.last_name) = LOWER(mp.plastname)
                            AND LOWER(mh.gender) = LOWER(mp.gender)
                            AND mh.birth_date = mp.dob
                            AND mh.mobile = mp.mobile
                            AND LOWER(mh.email) = LOWER(mp.email)
                        )
                    WHERE 
                        (mh.mr_number = %s OR %s IS NULL) AND
                        (LOWER(mh.first_name) = LOWER(%s) OR %s IS NULL) AND
                        (LOWER(mh.last_name) = LOWER(%s) OR %s IS NULL) AND
                        (LOWER(mh.gender) = LOWER(%s) OR %s IS NULL) AND
                        (mh.birth_date = %s OR %s IS NULL) AND
                        (mh.mobile = %s OR %s IS NULL) AND
                        (LOWER(mh.email) = LOWER(%s) OR %s IS NULL)
                    ORDER BY match_score DESC;
                """

                # Execute the SQL query with parameters from each patient
                cur.execute(query, (
                    mr_number, mr_number,
                    first_name, first_name,
                    last_name, last_name,
                    gender, gender,
                    birth_date, birth_date,
                    mobile, mobile,
                    email, email
                ))

                # Fetch results and write them to the CSV file
                results = cur.fetchall()
                if results:
                    for row in results:
                        writer.writerow(row)

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        # Ensure cursor and connection are closed if they were opened
        if conn:
            cur.close()
            conn.close()
            print("Database connection closed")

# Run the function to process all patients and write to CSV
search_patient()
