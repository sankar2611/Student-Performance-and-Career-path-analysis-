from flask import Flask, request, redirect, url_for, render_template
import db 

app = Flask(__name__)

@app.route('/')

def index():
    return render_template("index.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/job')
def job():
    return render_template("job.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/signup')
def signup():
    return render_template("sign.html")

@app.route('/details')
def details():
    return render_template("studentdetails.html")



 # Assuming db.py contains your database functions
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form['name']
    email = request.form['email']
    subject = request.form['subject']
    message = request.form['message']

    # Insert into the database using SQL Server
    db.insert_contact(name, email, subject, message)

    # Redirect or render a success page
    return redirect(url_for('contact'))


if __name__ ==  "__main__":
    app.run(debug=True, host="0.0.0.0")