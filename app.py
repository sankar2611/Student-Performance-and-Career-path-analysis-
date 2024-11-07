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

            db.log_user_login(email, role)

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
    return render_template('profile.html')

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

            db.log_user_login(email, role)

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
    

# app.py
from flask import Flask, jsonify
import pyodbc
import pandas as pd


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



# app.py
from flask import Flask, render_template
import pandas as pd

def load_data():
    data = {
        'id': [6, 7, 8, 9, 10, 11, 12, 13],
        'student_id': [5, 3, 3, 3, 3, 3, 5, 5],
        'subject': ['science', 'computer', 'math', 'biology', 'physics', 'chemistry', 'maths', 'computer'],
        'cgpa': [2.4, 5.0, 6.5, 7.0, 6.5, 7.0, 9.0, 8.5]
    }
    return pd.DataFrame(data)

def analyze_student(df, student_id):
    # Filter data for specific student
    student_data = df[df['student_id'] == student_id]
    
    # Get top subjects based on CGPA
    top_subjects = student_data.sort_values('cgpa', ascending=False)
    
    # Calculate average CGPA
    avg_cgpa = student_data['cgpa'].mean()
    
    # Determine strengths and recommend roles
    strengths = []
    recommendations = []
    
    for _, row in top_subjects.iterrows():
        if row['cgpa'] >= 7.0:
            strengths.append(f"{row['subject'].title()} (CGPA: {row['cgpa']})")
    
    # Job recommendations based on top subjects
    if 'computer' in student_data['subject'].values and student_data[student_data['subject'] == 'computer']['cgpa'].values[0] >= 7.0:
        recommendations.extend(['Software Developer', 'Data Analyst', 'IT Consultant'])
    
    if any(subj in student_data['subject'].values for subj in ['math', 'maths']) and \
       student_data[student_data['subject'].isin(['math', 'maths'])]['cgpa'].values[0] >= 7.0:
        recommendations.extend(['Data Scientist', 'Financial Analyst', 'Research Analyst'])
    
    if 'science' in student_data['subject'].values and student_data[student_data['subject'] == 'science']['cgpa'].values[0] >= 7.0:
        recommendations.append('Research Scientist')
    
    if 'biology' in student_data['subject'].values and student_data[student_data['subject'] == 'biology']['cgpa'].values[0] >= 7.0:
        recommendations.extend(['Biotechnologist', 'Medical Researcher'])
        
    if 'physics' in student_data['subject'].values and student_data[student_data['subject'] == 'physics']['cgpa'].values[0] >= 7.0:
        recommendations.extend(['Physics Researcher', 'Engineering Roles'])
        
    if 'chemistry' in student_data['subject'].values and student_data[student_data['subject'] == 'chemistry']['cgpa'].values[0] >= 7.0:
        recommendations.extend(['Chemical Engineer', 'Lab Researcher'])
    
    return {
        'student_id': student_id,
        'strengths': strengths,
        'recommendations': list(set(recommendations)),  # Remove duplicates
        'avg_cgpa': round(avg_cgpa, 2),
        'all_subjects': top_subjects.to_dict('records')
    }

@app.route('/trial')
def trial():
    df = load_data()
    student_ids = df['student_id'].unique()
    all_analyses = []
    
    for student_id in student_ids:
        analysis = analyze_student(df, student_id)
        all_analyses.append(analysis)
    
    return render_template('trial.html', analyses=all_analyses)


    



 
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")