from flask import Flask, request, redirect, url_for, render_template, session, flash,jsonify
from datetime import timedelta
from functools import wraps
import db 

app = Flask(__name__)
app.secret_key = '2144bf28b53d00814d9f82b0ef0e0857'  # Set a secret key for session management


app.permanent_session_lifetime = timedelta(minutes=30)


@app.route('/')
def home():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        role, user = db.check_user(email, password)
        print(f"DEBUG: Role: {role}, User: {user}")  

        if user:
            session['email'] = email
            session['name'] = user[1]  
            session['role'] = role.lower()
            session['user_id'] = user[0] 
            print("DEBUG: Session set")  

            db.log_user_login(email, role,user[0])

            flash('Login successful!', 'success')            
            if role.lower() == 'student':
                return redirect(url_for('index'))
            elif role.lower() == 'company':
                return redirect(url_for('company'))
        else:
            # Invalid credentials
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('login'))
    return render_template("login.html")

@app.route('/job')
def job():
    return render_template('jobpage.html')

@app.route('/profile')
def profile():
    user = session.get('user_id')  # Email is already in the session

    return render_template('profile.html', user=user)

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/contact')
def contact():
    if 'email' not in session:
        flash("You need to be logged in to access this page.", "error")
        return redirect(url_for('login'))
    user_name = session.get('name')  # Assuming you set 'name' in the session during login
    user_email = session.get('email')  # Email is already in the session

    return render_template("contact.html", name=user_name, email=user_email)

@app.route('/course')
def course():
    return render_template("course.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check which table the user exists in
        role, user = db.check_user(email, password)
        if user:
            session['email'] = email
            session['name'] = user[1]
            session['role'] = role.lower()
            session['user_id'] = user[0]

            db.log_user_login(email, role,user[0])

            flash('Login successful!', 'success')            
            if role.lower() == 'student':
                return redirect(url_for('index'))
            elif role.lower() == 'company':
                return redirect(url_for('company'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('login'))
    return render_template("login.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        # Insert into the database
        result = db.insert_signup(name, contact, email, password, role)

        # Flash success or error message
        if result == "Signup successful":
            flash("Signup successful! Welcome, {}".format(name))
            return redirect('/login')  # Redirect to the login page after successful signup
        elif result == "Email already exists":
            flash("Error: Email already exists.")
        else:
            flash("Error during signup, please try again.")

        return redirect('/signup')  # This can stay for errors

    return render_template("sign.html")  # Render the signup page for GET requests

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    user_role = session.get('role')  # Retrieve the user role from the session

    if user_role == 'student':
        # Insert into the database using the student contact method
        db.insert_contact(name, email, subject, message)
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))
    elif user_role == 'company':
        # Insert into the database using the company contact method
        db.insert_contact_company(name, email, subject, message)
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact2'))
        
    else:
        flash('Error: User role not recognized. Please log in again.', 'error')
        return redirect(url_for('login'))  # Redirect if the role is not recognized

    

    # Redirect or render a success page
    

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/details', methods=['GET', 'POST'])
@login_required
def student_details():
    if 'email' not in session:
        flash("You need to be logged in to access this page.", "error")
        return redirect(url_for('login'))
    
    user_id = session.get('user_id')
    
    # if not user_id:
    #     flash("You need to be logged in to access this page.", "error")
    #     return redirect(url_for('login'))

    user_details = db.get_user_details(user_id)
    if not user_details:
        flash("User details not found. Please contact support.", "error")
        return redirect(url_for('contact'))
    if request.method == 'POST':
        # Extract form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        middle_name = request.form.get('middle_name', '')  # Optional field
        date_of_birth = request.form['date_of_birth']
        mobile_number = request.form['mobile_number']
        gender = request.form['gender']
        area_of_interest = request.form['area_of_interest']
        location = request.form['location']
        nationality = request.form['nationality']
        preferred_location = request.form['preferred_location']
        job_mode = request.form['job_mode']
        available_to_join = request.form['available_to_join']
        skills = request.form['skills']
        languages = request.form['languages']
        university = request.form['university']
        course = request.form['course']
        specialization = request.form['specialization']
        course_start = request.form['course_start']
        course_end = request.form['course_end']
        github = request.form.get('github', '') 
        print("done") # Optional field
        linkedin = request.form['linkedin']
        
        # Extract subjects and CGPAs
        subjects = request.form.getlist('subject-name[]')
        cgpas = request.form.getlist('cgpa[]')

        # Insert data into the database using the student_id from session
        result = db.insert_student_details(
            user_id, first_name, last_name, middle_name, date_of_birth, mobile_number, 
            gender, area_of_interest, location, nationality, preferred_location, 
            job_mode, available_to_join, skills, languages, university, course, 
            specialization, course_start, course_end, github, linkedin, 
            subjects, cgpas
        )
        import logging

        logging.basicConfig(level=logging.DEBUG)

        # Instead of print(), use:
        logging.debug(f"Form Data: {first_name}, {last_name}, {middle_name}, {date_of_birth}, {mobile_number}, "
                    f"{gender}, {area_of_interest}, {location}, {nationality}, {preferred_location}, "
                    f"{job_mode}, {available_to_join}, {skills}, {languages}, {university}, {course}, "
                    f"{specialization}, {course_start}, {course_end}, {github}, {linkedin}, {subjects}, {cgpas}")

        if result == "Details submitted successfully":
            print("Successfully")
            flash("Your details have been submitted successfully!", "success")
            return redirect(url_for('index'))  # Redirect to home page or dashboard
        else:
            flash("Error submitting details. Please try again.", "error")
            return redirect(url_for('index'))

    # Render the template with user details pre-filled
    return render_template("studentdetails.html", user=user_details)



@app.route('/company')
def company():
    return render_template("company.html")

@app.route('/dash')
def dash():
    return render_template("dash.html")

@app.route('/post', methods=['GET', 'POST'])
# @login_required
def post():
    # if 'email' not in session:
    #     flash("You need to be logged in to access this page.", "error")
    #     return redirect(url_for('login'))
    # user_email = session.get('email')  # Email is already in the session
    if request.method == 'POST':
        job_title = request.form['job_title']
        job_description = request.form['job_description']
        requirements = request.form['requirements']
        min_salary = request.form['min_salary']
        max_salary = request.form['max_salary']
        location = request.form['location']
        job_type = request.form['job_type']
        application_deadline = request.form['application_deadline']
        company_id = session.get('user_id') 
        contact = request.form['contact'] 
        # Call the function to add the job posting to the database
        db.add_job_posting(job_title, job_description, requirements, min_salary, max_salary, location, job_type, application_deadline, contact, company_id)

        return redirect(url_for('company'))
    return render_template("post.html")



@app.route('/contact2', methods=['GET', 'POST'])
def contact2():
    if 'email' not in session:
        flash("You need to be logged in to access this page.", "error")
        return redirect(url_for('login'))

    if request.method == 'GET':
        # Fetch user details from session for pre-filling
        user_name = session.get('name')
        user_email = session.get('email')
        return render_template("contact copy.html", name=user_name, email=user_email)

    # Handle form submission for contact2 and save to `contact_company` table
    if request.method == 'POST':
        subject = request.form['subject']
        message = request.form['message']
        name = session.get('name')
        email = session.get('email')

        # Insert into `contact_company` table in the database
        db.insert_contact_company(name, email, subject, message)
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('company'))
    
@app.route('/update/<job_id>', methods=['PUT'])
@login_required
def update_job(job_id):
    if 'email' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    job_title = data['jobTitle']
    job_description = data['jobDescription']
    job_requirements = data['jobRequirements']
    salary_range = data['salaryRange']
    min_salary, max_salary = salary_range.split(' - ')
    location = data['location']
    job_type = data['jobType']
    application_deadline = data['applicationDeadline']
    contact = data['contact']

    # Call the function to update the job in the database
    db.update_job_posting(job_id, job_title, job_description, job_requirements, min_salary, max_salary,
                          location, job_type, application_deadline, contact)

    return jsonify({"success": True})

@app.route('/delete/<job_id>', methods=['DELETE'])
@login_required
def delete_job(job_id):
    if 'email' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    # Call the function to move the job posting to the deleted jobs table
    db.delete_job_posting(job_id)

    return jsonify({"success": "Job deleted successfully."}), 200




# app.py
from flask import Flask, jsonify
import pyodbc
import pandas as pd
from datetime import datetime


# Database connection details (without username and password)
server = 'MEMRS'
database = 'student-career-performance-analysis'

# Connect to SQL Server
def get_database_connection():
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    )
    return conn

@app.route('/api/gender_distribution', methods=['GET'])
def gender_distribution():
    # Fetch data from SQL Server
    conn = get_database_connection()
    query = "SELECT gender FROM StudentDetails"  # Modify with your table name and relevant columns
    data = pd.read_sql(query, conn)
    conn.close()
    
    # Calculate gender distribution
    gender_counts = data['gender'].value_counts()
    
    # Prepare data for JSON response
    gender_data = {
        "labels": gender_counts.index.tolist(),
        "counts": gender_counts.values.tolist()
    }
    
    return jsonify(gender_data)


def calculate_age(dob):
    today = datetime.today()
    age = today.year - dob.year
    # Adjust if the current date is before the birthday in the current year
    if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
        age -= 1
    return age

# Categorizing age into ranges
def categorize_age(age):
    if age<18:
        return 'Less than 18'
    elif 18 <= age <= 20:
        return '18-20'
    elif 21 <= age <= 25:
        return '21-25'
    elif 26 <= age <= 35:
        return '26-35'
    elif 36 <= age <= 45:
        return '36-45'
    elif 46 <= age <= 60:
        return '46-60'
    elif age > 60:
        return '60+'
    return 'Unknown'

@app.route('/api/age_distribution', methods=['GET'])
def age_distribution():
    # Fetch data from SQL Server
    conn = get_database_connection()
    query = "SELECT date_of_birth FROM StudentDetails"  # Modify with your table name and relevant columns
    data = pd.read_sql(query, conn)
    conn.close()
    
    # Calculate age distribution
    data['age'] = data['date_of_birth'].apply(calculate_age)
    data['age_group'] = data['age'].apply(categorize_age)
    
    # Calculate the counts for each age group
    age_counts = data['age_group'].value_counts()
    
    # Prepare data for JSON response
    age_data = {
        "labels": age_counts.index.tolist(),
        "counts": age_counts.values.tolist()
    }
    
    return jsonify(age_data)

@app.route('/api/job_mode_distribution', methods=['GET'])
def job_mode_distribution():
    # Fetch data from SQL Server
    conn = get_database_connection()
    query = "SELECT job_mode FROM StudentDetails"  # Modify with your table name and relevant columns
    data = pd.read_sql(query, conn)
    conn.close()
    
    # Calculate job mode distribution (assumes job_mode column exists)
    job_mode_counts = data['job_mode'].value_counts()
    
    # Prepare data for JSON response
    job_mode_data = {
        "labels": job_mode_counts.index.tolist(),  # job modes like 'Full-time', 'Part-time'
        "counts": job_mode_counts.values.tolist()
    }
    
    return jsonify(job_mode_data)

@app.route('/api/available_to_join_distribution', methods=['GET'])
def available_to_join_distribution():
    conn = get_database_connection()
    query = "SELECT available_to_join FROM StudentDetails"  # Modify with your table name and relevant columns
    data = pd.read_sql(query, conn)
    conn.close()
    
    # Calculate available to join distribution
    available_to_join_counts = data['available_to_join'].value_counts()

    # Prepare data for JSON response
    available_to_join_data = {
        "labels": available_to_join_counts.index.tolist(),
        "counts": available_to_join_counts.values.tolist()
    }
    
    return jsonify(available_to_join_data)

@app.route('/api/user_distribution', methods=['GET'])
def user_distribution():
    # Fetch data from SQL Server for student_users and company_users
    conn = get_database_connection()

    # Query to get the count of users in student_users and company_users
    query_student_users = "SELECT COUNT(*) AS student_count FROM Sign_up"
    query_company_users = "SELECT COUNT(*) AS company_count FROM Sign_up_company"

    # Execute queries and fetch the results
    student_data = pd.read_sql(query_student_users, conn)
    company_data = pd.read_sql(query_company_users, conn)

    conn.close()

    # Convert Pandas int64 to Python int
    student_count = student_data['student_count'][0].item()
    company_count = company_data['company_count'][0].item()

    # Prepare data for JSON response
    user_data = {
        "labels": ["Student Users", "Company Users"],
        "counts": [student_count, company_count]
    }

    return jsonify(user_data)


   


# app.py
from flask import Flask, render_template
import pandas as pd

def load_data():
    
    # Establish connection to the database
    connection = get_database_connection()
    
    # SQL query to fetch data (replace with your query)
    query = 'SELECT * FROM StudentSubjects'

    # Use pandas to load the query result into a DataFrame
    data = pd.read_sql(query, connection)
    
    # Close the connection
    connection.close()

    return data

# Load the data
data_from_db = load_data()
print(data_from_db)

def login_student(connection, student_id):
    """Authenticate student based on student_id."""
    # Check if the student exists in the signup table
    signup_query = f"SELECT * FROM Sign_up WHERE id = {student_id}"
    student_info = pd.read_sql(signup_query, connection)
    
    if student_info.empty:
        return None  # Student not found
    return student_info  # Student found, return their details

def analyze_student(connection, student_id):
    """Analyze student based on their subject data after login."""
    # Check student login
    student_info = login_student(connection, student_id)
    if student_info is None:
        return {'error': 'Invalid student ID or student not found.'}
    
    # Fetch student's subject data from the subjects table
    subject_query = f"SELECT * FROM StudentSubjects WHERE student_id = {student_id}"
    student_data = pd.read_sql(subject_query, connection)
    
    if student_data.empty:
        return {'error': 'No subject data found for the student.'}
    
    # Get top subjects based on CGPA
    top_subjects = student_data.sort_values('cgpa', ascending=False)
    
    # Calculate average CGPA
    avg_cgpa = student_data['cgpa'].mean()
    
    # Determine strengths and recommend roles
    strengths = []
    recommendations = []
    
    for _, row in top_subjects.iterrows():
        if row['cgpa'] >= 7.0:
            strengths.append(f"{row['subject_name'].title()} (CGPA: {row['cgpa']})")
    
    # Job recommendations based on top subjects
    if 'computer' in student_data['subject_name'].values and student_data[student_data['subject_name'] == 'computer']['cgpa'].values[0] >= 7.0:
        recommendations.extend(['Software Developer', 'Data Analyst', 'IT Consultant'])
    
    if any(subj in student_data['subject_name'].values for subj in ['math', 'maths']) and \
       student_data[student_data['subject_name'].isin(['math', 'maths'])]['cgpa'].values[0] >= 7.0:
        recommendations.extend(['Data Scientist', 'Financial Analyst', 'Research Analyst'])
    
    if 'science' in student_data['subject_name'].values and student_data[student_data['subject_name'] == 'science']['cgpa'].values[0] >= 7.0:
        recommendations.append('Research Scientist')
    
    if 'biology' in student_data['subject_name'].values and student_data[student_data['subject_name'] == 'biology']['cgpa'].values[0] >= 7.0:
        recommendations.extend(['Biotechnologist', 'Medical Researcher'])
        
    if 'physics' in student_data['subject_name'].values and student_data[student_data['subject_name'] == 'physics']['cgpa'].values[0] >= 7.0:
        recommendations.extend(['Physics Researcher', 'Engineering Roles'])
        
    if 'maths' in student_data['subject_name'].str.lower().values and student_data[student_data['subject_name'].str.lower() == 'maths']['cgpa'].values[0] >= 5.0:
        recommendations.extend(['Chemical Engineer', 'Lab Researcher'])


    
    
    return {
        'student_id': student_id,
        'student_name': student_info['name'].values[0],
        'strengths': strengths,
        'recommendations': list(set(recommendations)),  # Remove duplicates
        'avg_cgpa': round(avg_cgpa, 2),
        'all_subjects': top_subjects.to_dict('records')
    }

@app.route('/trial/<int:student_id>', methods=['GET'])
def student_analysis(student_id):
    """Fetch and analyze student data based on student_id from URL path"""
    # Debugging: Print the student ID to check if it's being passed correctly
    print(f"Student ID: {student_id}")

    # Proceed with your logic to connect to the database and fetch data
    db_connection = get_database_connection()

    # Analyze the student's data
    result = analyze_student(db_connection, student_id)
    
    # Close the database connection
    db_connection.close()

    if not result:
        return render_template('error.html', message="Student not found or no data available")

    # Pass the results to the HTML template
    return render_template('trial.html', **result)


 
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")