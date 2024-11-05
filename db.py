import pyodbc
from werkzeug.security import generate_password_hash,check_password_hash


def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'  # Make sure to have the correct ODBC driver installed
        'SERVER=MEMRS;'  # Replace with your server name or IP address
        'DATABASE=student-career-performance-analysis;'
        'Trusted_Connection=yes;'
        'Encrypt=yes;'  # Optional: Forces encryption (if you need)
        'TrustServerCertificate=yes;'  # Bypasses the SSL certificate validation
    )
    return conn
def insert_contact(name, email, subject, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Contact (Name, Email, Subject, Message) 
        VALUES (?, ?, ?, ?)
    ''', (name, email, subject, message))
    conn.commit()
    cursor.close()
    conn.close()
def check_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check in the student table
    cursor.execute("SELECT * FROM Sign_up WHERE email=?", (email,))
    student = cursor.fetchone()

    if student is not None:
        print(f"Found student: {student}")  # Debug log
        # Make sure the index here corresponds to the password column
        if check_password_hash(student[4], password):  # Adjust index as needed
            return 'student', student
        else:
            return None, None  # Password does not match

    # Check in the company table
    cursor.execute("SELECT * FROM Sign_up_company WHERE email=?", (email,))
    company = cursor.fetchone()

    if company is not None:
        print(f"Found company: {company}")  # Debug log
        # Make sure the index here corresponds to the password column
        if check_password_hash(company[4], password):  # Adjust index as needed
            return 'company', company
        else:
            return None, None  # Password does not match

    print("No user found")  # Debug log
    return None, None  # No user found
def log_user_login(email, role):
    conn=get_db_connection()
    cursor = conn.cursor()

    # Insert the login details into the User_Logins table
    cursor.execute("INSERT INTO user_logins (email, role) VALUES (?, ?)", (email, role))

    # Commit the transaction
    conn.commit()
    cursor.close()
    conn.close()
def insert_signup(name, contact, email, password, role):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if email already exists in either table
        cursor.execute('''
            SELECT name, contact, email, id  FROM Sign_up WHERE email=?
            UNION
            SELECT name, contact, email, company_id AS id FROM Sign_up_company WHERE email=?
        ''', (email, email))

        if cursor.fetchone():
            # Email already exists
            print("DEBUG: Email already exists in database")  # Add logging for debugging
            return "Email already exists"
        password = generate_password_hash(password)
        # Proceed with the sign-up process based on the role
        if role.lower() == 'student':
            cursor.execute('''
                INSERT INTO Sign_up (name, contact, email, password)
                VALUES (?, ?, ?, ?)
            ''', (name, contact, email, password))
        elif role.lower() == 'company':
            cursor.execute('''
                INSERT INTO Sign_up_company (name, contact, email, password)
                VALUES (?, ?, ?, ?)
            ''', (name, contact, email, password))

        conn.commit()
        # print("DEBUG: Signup successful")  # Logging success
        return "Signup successful"

    except Exception as e:
        # print(f"DEBUG: Error during signup: {e}")  # Log any errors
        return "Error during signup"

    finally:
        cursor.close()
        conn.close()
def insert_student_details(student_id, first_name, last_name, middle_name, date_of_birth, mobile_number, 
                           gender, area_of_interest, location, nationality, preferred_location, 
                           job_mode, available_to_join, skills, languages, university, course, 
                           specialization, course_start, course_end, github, linkedin, 
                           subjects, cgpas):
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Inserting student details")
    try:
        print("try coming")
        # Insert into StudentDetails table, link it with the Sign_up ID (student_id)
        cursor.execute('''
            INSERT INTO StudentDetails (
                student_id, first_name, last_name, middle_name, date_of_birth, mobile_number, 
                gender, area_of_interest, location, nationality, preferred_location, 
                job_mode, available_to_join, skills, languages, university, course, 
                specialization, course_start, course_end, github, linkedin
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
        ''', (student_id, first_name, last_name, middle_name, date_of_birth, mobile_number, 
              gender, area_of_interest, location, nationality, preferred_location, 
              job_mode, available_to_join, skills, languages, university, course, 
              specialization, course_start, course_end, github, linkedin))
        print("Data Insertion into StudentDetails successful")

        # Insert subjects and CGPAs
        if subjects and cgpas:
            for subject, cgpa in zip(subjects, cgpas):
                cursor.execute('''
                    INSERT INTO StudentSubjects (student_id, subject_name, cgpa)
                    VALUES (?, ?, ?)
                ''', (student_id, subject, cgpa))
        print("done")
        conn.commit()
        return "Details submitted successfully"

    except Exception as e:
        conn.rollback()
        print(f"Error inserting student details: {e}")
        return "Error submitting details"

    finally:
        cursor.close()
        conn.close()
def get_user_details(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT name, contact FROM Sign_up WHERE id = ?
        ''', (user_id))
        user_details = cursor.fetchone()

        if user_details:
            print("found")
            return {'name': user_details[0], 'contact': user_details[1]}
        else:
            return None

    except Exception as e:
        print(f"Error fetching user details: {e}")
        return None

    finally:
        cursor.close()
        conn.close()
def insert_contact_company(name, email, subject, message):
    print("Attempting to insert data into contact_company...")  # Debugging message
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO contact_company (name, email, subject, message, date)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (name, email, subject, message))
        conn.commit()  # Commit the transaction
        print("Data inserted successfully into contact_company table.")
    except :
        print("An error occurred while inserting data:")
    finally:
        conn.close()
        print("Database connection closed.")
def add_job_posting(job_title, job_description, requirements, min_salary, max_salary, location, job_type, application_deadline, contact, company_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    try:
        sql = '''
        INSERT INTO jobs (company_id, job_title, job_description, requirements, min_salary, max_salary, location, job_type, application_deadline, contact)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        values = (company_id, job_title, job_description, requirements, min_salary, max_salary, location, job_type, application_deadline, contact)
        cursor.execute(sql, values)
        connection.commit()
        print("Job posting inserted successfully.")  # Debug message
    except Exception as e:
        print(f"Error inserting job posting: {e}")  # Log any exceptions
    finally:
        cursor.close()
        connection.close()
