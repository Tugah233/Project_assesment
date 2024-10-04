import os
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

# Function to export matches to CSV
def export_to_csv(data):
    import csv
    with open('matches.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "mr_number", "first_name", "last_name", "fullname", "gender", "birth_date", "mobile", "email", 
            "patient_id", "pfirst_name", "plast_name", "pfullname", "pgender", "pdob", "housemobile", "officemobile", "pmobile", "pemail",
            "mr_number_score", "first_name_score", "last_name_score", "fullname_score", "gender_score", 
            "birth_date_score", "mobile_score", "housemobile_score", "officemobile_score", "email_score", "match_score"
        ])
        for row in data:
            writer.writerow(row)
    print("Results exported to matches.csv")

# Function to prompt user for parameter selection and input
def prompt_for_search_parameter():
    print("Which parameter do you want to search by?")
    print("1. MR Number")
    print("2. First Name")
    print("3. Last Name")
    print("4. Full Name")
    print("5. Birth Date")
    print("6. Mobile")

    choice = input("Enter the number of the parameter (1-6): ")
    param_mapping = {
        "1": "mr_number",
        "2": "first_name",
        "3": "last_name",
        "4": "fullname",
        "5": "birth_date",
        "6": "mobile"
    }

    if choice in param_mapping:
        param = param_mapping[choice]
        value = input(f"Enter the {param}: ")
        return param, value
    else:
        print("Invalid selection. Please try again.")
        return prompt_for_search_parameter()

# Function to search for a patient based on user input and display the results
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

        # Prompt the user for a search parameter
        search_param, search_value = prompt_for_search_parameter()

        # SQL query to search for matches based on the selected parameter
        query = f"""
            SELECT
                mh.mr_number,
                mh.first_name,
                mh.last_name,
                mh.first_name || ' ' || mh.last_name AS fullname,
                mh.gender,
                mh.birth_date,
                mh.mobile,
                mh.email,
                mp.patient_id,
                mp.pfirstname AS pfirst_name,
                mp.plastname AS plast_name,
                mp.pfirstname || ' ' || mp.plastname AS pfullname,
                mp.gender AS pgender,
                mp.dob AS pdob,
                mp.housetelephoneno AS housemobile,
                mp.officetelephoneno AS officemobile,
                mp.mobile AS pmobile,
                mp.email AS pemail,
                CASE WHEN mh.mr_number = mp.patient_id THEN 10 ELSE 0 END AS mr_number_score,
                CASE WHEN LOWER(mh.first_name) = LOWER(mp.pfirstname) THEN 3 ELSE 0 END AS first_name_score,
                CASE WHEN LOWER(mh.last_name) = LOWER(mp.plastname) THEN 5 ELSE 0 END AS last_name_score,
                CASE WHEN LOWER(mh.first_name || ' ' || mh.last_name) = LOWER(mp.pfirstname || ' ' || mp.plastname) THEN 8 ELSE 0 END AS fullname_score,
                CASE WHEN LOWER(mh.gender) = LOWER(mp.gender) THEN 1 ELSE 0 END AS gender_score,
                CASE WHEN mh.birth_date = mp.dob THEN 4 ELSE 0 END AS birth_date_score,
                CASE WHEN mh.mobile = mp.mobile THEN 3 ELSE 0 END AS mobile_score,
                CASE WHEN mh.mobile = mp.housetelephoneno THEN 3 ELSE 0 END AS housemobile_score,
                CASE WHEN mh.mobile = mp.officetelephoneno THEN 3 ELSE 0 END AS officemobile_score,
                CASE WHEN LOWER(mh.email) = LOWER(mp.email) THEN 5 ELSE 0 END AS email_score,
                (
                    CASE WHEN mh.mr_number = mp.patient_id THEN 10 ELSE 0 END +
                    CASE WHEN LOWER(mh.first_name) = LOWER(mp.pfirstname) THEN 3 ELSE 0 END +
                    CASE WHEN LOWER(mh.last_name) = LOWER(mp.plastname) THEN 5 ELSE 0 END +
                    CASE WHEN LOWER(mh.first_name || ' ' || mh.last_name) = LOWER(mp.pfirstname || ' ' || mp.plastname) THEN 8 ELSE 0 END +
                    CASE WHEN LOWER(mh.gender) = LOWER(mp.gender) THEN 1 ELSE 0 END +
                    CASE WHEN mh.birth_date = mp.dob THEN 4 ELSE 0 END +
                    CASE WHEN mh.mobile = mp.mobile THEN 3 ELSE 0 END +
                    CASE WHEN mh.mobile = mp.housetelephoneno THEN 3 ELSE 0 END +
                    CASE WHEN mh.mobile = mp.officetelephoneno THEN 3 ELSE 0 END +
                    CASE WHEN LOWER(mh.email) = LOWER(mp.email) THEN 5 ELSE 0 END
                ) AS match_score
            FROM 
                medihealth__patients mh
            LEFT JOIN 
                mis__patients mp
            ON 
                mh.mr_number = mp.patient_id
                OR LOWER(mh.first_name) = LOWER(mp.pfirstname)
                OR LOWER(mh.last_name) = LOWER(mp.plastname)
                OR LOWER(mh.first_name || ' ' || mh.last_name) = LOWER(mp.pfirstname || ' ' || mp.plastname)
                OR mh.birth_date = mp.dob
                OR mh.mobile = mp.mobile
                OR mh.mobile = mp.housetelephoneno
                OR mh.mobile = mp.officetelephoneno
                OR LOWER(mh.email) = LOWER(mp.email)
            WHERE 
                LOWER(mh.{search_param}) = LOWER(%s)
            ORDER BY match_score DESC;
        """

        # Execute the SQL query with the search value
        cur.execute(query, (search_value,))
        results = cur.fetchall()

        # Display match results
        match_count = len(results)
        if match_count > 0:
            print(f"\n{match_count} matches found for '{search_param}': {search_value}\n")
            print("Breakdown of matches:")
            for row in results:
                print(f"MR Number: {row[0]}, First Name: {row[1]}, Last Name: {row[2]}, Full Name: {row[3]}, Gender: {row[4]}, Mobile: {row[6]}, Match Score: {row[-1]}")
        else:
            print(f"No matches found for '{search_param}': {search_value}")

        # Ask if the results should be exported to a CSV
        export_choice = input("\nDo you want to export the results to a CSV? (Y/N): ").strip().upper()
        if export_choice == 'Y':
            export_to_csv(results)

    except Exception as e:
        print(f"Error occurred: {e}")

    finally:
        if conn:
            cur.close()
            conn.close()
            print("Database connection closed.")

# Run the function when needed
if __name__ == "__main__":
    search_patient()
