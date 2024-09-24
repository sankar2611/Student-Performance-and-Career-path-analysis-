from flask import Flask, request, redirect, url_for, render_template, session, flash
import db 

app = Flask(__name__)
app.secret_key = '2144bf28b53d00814d9f82b0ef0e0857'  # Set a secret key for session management


@app.route('/')
def home():
    return render_template("login.html")

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

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
            # Store user details in session
            session['email'] = email
            session['role'] = role.lower()
            print("DEBUG: Session set")  # Debugging session

            db.log_user_login(email, role)

            # Redirect to respective dashboard
            if role.lower() == 'student':
                return redirect(url_for('index'))
            elif role.lower() == 'company':
                return redirect(url_for('index'))
        else:
            # Invalid credentials
            print("DEBUG: Invalid credentials")  # Log invalid login attempts
            return "Invalid credentials", 401

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

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")