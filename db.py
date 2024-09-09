import pyodbc

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
