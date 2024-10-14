from flask import Flask, request, redirect, url_for, render_template, session, flash
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
                return redirect(url_for('index'))
        else:
            # Invalid credentials
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('login'))
    return render_template("login.html")

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

@app.route('/job')
def job():
    return render_template("job.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check which table the user exists in
        role, user = db.check_user(email, password)
        print(f"DEBUG: Role: {role}, User: {user}")  # Add debug information

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
                return redirect(url_for('index'))
        else:
            # Invalid credentials
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

@app.route('/student_dashboard')
def student_dashboard():
    if 'email' in session and session['role'] == 'student':
        return "Student Dashboard"
    else:
        return redirect(url_for('login'))

@app.route('/company_dashboard')
def company_dashboard():
    if 'email' in session and session['role'] == 'company':
        return "Company Dashboard"
    else:
        return redirect(url_for('login'))

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    # Insert into the database using SQL Server
    db.insert_contact(name, email, subject, message)
    flash('Your message has been sent successfully!', 'success')

    # Redirect or render a success page
    return redirect(url_for('contact'))

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

@app.route('/post')
def post():
    return render_template("post.html")

@app.route('/contact2')
def contact2():
    return render_template("contact copy.html")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")