from flask import Flask, render_template, request, session, redirect
from pymongo import MongoClient  # used for mongodb connection
import bcrypt  # used for password hashing
from flask_limiter import Limiter  # used to limit login attempts
from flask_limiter.util import get_remote_address
from functools import wraps  # used to create login_required decorator
from dotenv import load_dotenv  # load environment variables from .env
import os
import secrets  # generate secure random secret key
from flask_wtf.csrf import CSRFProtect  # protects against CSRF attacks
import re  # used for input validation (regex)

# Load variables from .env file
load_dotenv()

# Create Flask application
app = Flask(__name__)

# Secret key used for session security
# Loaded from .env instead of hardcoding for security
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

# Enable CSRF protection for all forms
# Prevents cross-site request forgery attacks
csrf = CSRFProtect(app)

# Get MongoDB connection string from .env
MONGO_URI = os.getenv("MONGO_URI")

# Stop application if database URL missing
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not found in .env file")

# Connect to MongoDB database
client = MongoClient(MONGO_URI)

# Select database
db = client["hr_erp_db"]

# Collections
employee_collection = db["registration"]
admin_collection = db["admin"]

# Create indexes for faster searching and unique employee id
employee_collection.create_index("emp_id", unique=True)
employee_collection.create_index("name")

# Limit login attempts to prevent brute force attacks
limiter = Limiter(get_remote_address, app=app)


# Input validation function
# Ensures employee data is correct before saving to database
def validate_employee(name, mobile, email, salary):
    errors = []

    # Validate name
    if not name or not re.match(r"^[A-Za-z0-9\s]{2,50}$", name.strip()):
        errors.append("Name must be 2–50 characters")

    # Validate mobile number
    if not re.match(r"^\d{10}$", mobile.strip()):
        errors.append("Mobile must be 10 digits")

    # Validate email format
    if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email.strip()):
        errors.append("Invalid email address")

    # Validate salary
    try:
        if float(salary) <= 0:
            errors.append("Salary must be positive")
    except ValueError:
        errors.append("Salary must be a number")

    return errors


# Decorator used to protect admin routes
# Prevents access without login
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "login" not in session:
            return redirect("/adminLogin")

        return func(*args, **kwargs)

    return wrapper


# Home page route
@app.route("/")
def home():
    return render_template("index.html")


# About page route
@app.route("/about")
def about_page():
    return render_template("aboutUs.html")


# Admin login page
@app.route("/adminLogin")
def adminlogin_page():
    return render_template("adminlogin.html")


# Contact page
@app.route("/contact", methods=["GET", "POST"])
def contact():
    success = False
    errors = []
    form_data = {}

    if request.method == "POST":

        name = request.form["txtname"]
        email = request.form["txtemail"]
        message = request.form["txtmessage"]

        form_data = request.form

        # Validate form fields
        if not name:
            errors.append("Name required")

        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email):
            errors.append("Invalid email")

        if len(message.strip()) < 10:
            errors.append("Message too short")

        if not errors:
            success = True

    return render_template("contactus.html", success=success, errors=errors, form_data=form_data)


# Admin login + dashboard
@app.route("/admindashboard", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # limits login attempts
def admin_dashboard_page():
    if request.method == "POST":

        username = request.form["txtname"]
        password = request.form["txtpassword"]

        # Find admin in database
        admin = admin_collection.find_one({"username": username})

        if admin:

            stored_password = admin["password"]

            # Compare entered password with hashed password
            if bcrypt.checkpw(password.encode("utf-8"), stored_password):
                # Create login session
                session["login"] = username
                session["name"] = "Admin"

                total_count = employee_collection.count_documents({})

                return render_template("admindashboard.html", total=total_count)

        # Invalid login
        msg = "Invalid username or password"
        return render_template("adminlogin.html", message=msg)

    else:

        # If already logged in show dashboard
        if "login" in session:
            total_count = employee_collection.count_documents({})
            return render_template("admindashboard.html", total=total_count)

        return render_template("adminlogin.html")


# Add employee page
@app.route("/adminaddemployee")
@login_required
def admin_addemployee_page():
    return render_template("admin_addemp.html")


# Save employee data
@app.route("/save", methods=["POST"])
@login_required
def save():
    empid = request.form["txtEmpID"]
    name = request.form["txtName"]
    mobile = request.form["txtMobile"]
    email = request.form["txtEmailID"]
    designation = request.form["txtDesignation"]
    salary = request.form["txtSalary"]

    # Validate input before saving
    errors = validate_employee(name, mobile, email, salary)

    if errors:
        return render_template("admin_addemp.html", errors=errors, form_data=request.form)

    # Duplicate ID → go to error.html
    existing = employee_collection.find_one({"emp_id": empid})
    if existing:
        errors.append("Employee ID already exists")
        return render_template("error.html", errors=errors)

    employee = {
        "emp_id": empid,
        "name": name,
        "mobile": mobile,
        "email": email,
        "designation": designation,
        "salary": salary
    }

    employee_collection.insert_one(employee)

    return render_template("admin_reg_sucess.html")


# Show employees with pagination
@app.route("/adminshowemployee")
@login_required
def admin_showemployee_page():
    page = request.args.get("page", 1, type=int)
    per_page = 8

    skip = (page - 1) * per_page

    employees = employee_collection.find().skip(skip).limit(per_page)

    total = employee_collection.count_documents({})
    total_pages = (total + per_page - 1) // per_page

    return render_template("admin_showemp.html",
                           recordlist=employees,
                           page=page,
                           total_pages=total_pages)


# Employee profile
@app.route("/adminemp_profile")
@login_required
def admin_emp_profile_page():
    emp_id = request.args.get("eid")

    employee = employee_collection.find_one({"emp_id": emp_id})

    return render_template("admin_emp_profile.html", recordlist=employee)


# Update employee
@app.route("/adminemp_update", methods=["POST"])
@login_required
def admin_update_employee_page():
    empid = request.form["txtEmpID"]
    name = request.form["txtName"]
    mobile = request.form["txtMobile"]
    email = request.form["txtEmailID"]
    designation = request.form["txtDesignation"]
    salary = request.form["txtSalary"]

    errors = validate_employee(name, mobile, email, salary)

    if errors:
        return render_template("admin_emp_profile.html", errors=errors, form_data=request.form)

    employee_collection.update_one(
        {"emp_id": empid},
        {
            "$set": {
                "name": name,
                "mobile": mobile,
                "email": email,
                "designation": designation,
                "salary": salary
            }
        }
    )

    return render_template("adminemp_update_success.html")


# Delete employee
@app.route("/adminemp_delete")
@login_required
def admin_delete_employee_page():
    emp_id = request.args.get("eid")

    employee_collection.delete_one({"emp_id": emp_id})

    return render_template("admin_emp_delete.html")


# Search employee page
@app.route("/adminSearchemployee")
@login_required
def admin_searchemployee_page():
    return render_template("admin_searchemp.html")


# Search employee result
@app.route("/adminSearchemp_result", methods=["POST"])
@login_required
def admin_search_employee_result_page():
    name = request.form["txtName"]

    employees = employee_collection.find({"name": name})

    return render_template("admin_searchemp_result.html", recordlist=employees)


# Logout admin
@app.route("/logout")
def logout_page():
    # Clear session when admin logs out
    session.clear()

    return render_template("adminlogin.html")


# Run Flask server
if __name__ == "__main__":
    app.run(debug=True)
