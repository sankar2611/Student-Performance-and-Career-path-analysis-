import pyodbc
from werkzeug.security import generate_password_hash,check_password_hash

# Define your connection parameters
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
        print("DEBUG: Signup successful")  # Logging success
        return "Signup successful"

    except Exception as e:
        print(f"DEBUG: Error during signup: {e}")  # Log any errors
        return "Error during signup"

    finally:
        cursor.close()
        conn.close()

