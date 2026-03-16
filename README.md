# Flask Employee Management System (ERP Style)

## Overview

This project is a **Flask-based Employee Management System** that allows an admin to manage employee records using a web interface.
It demonstrates backend development concepts such as authentication, security practices, and CRUD operations with MongoDB.

The system simulates a **basic ERP-style employee management module**.

---

## Features

* Admin Login Authentication
* Secure Password Hashing using bcrypt
* Session-based Authentication
* Employee CRUD Operations

  * Add Employee
  * View Employees
  * Update Employee
  * Delete Employee
* Employee Search
* Pagination for employee listing
* Input Validation using Regex
* CSRF Protection
* Rate Limiting for login security
* MongoDB Indexing for faster queries
* Environment Variable Security (.env)

---

## Tech Stack

**Backend**

* Python
* Flask

**Database**

* MongoDB

**Security**

* bcrypt
* Flask-Limiter
* Flask-WTF (CSRF Protection)

**Frontend**

* HTML
* CSS
* Jinja Templates

---

## Project Structure

```
project/
│
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── templates/
│   ├── adminlogin.html
│   ├── admindashboard.html
│   ├── admin_addemp.html
│   ├── admin_showemp.html
│   ├── admin_emp_profile.html
│   ├── admin_searchemp.html
│   ├── admin_searchemp_result.html
│   ├── admin_reg_success.html
│   └── index.html
│
├── static/
│
└── .env   (not uploaded to GitHub)
```

---

## Installation

### 1. Clone Repository

```
git clone https://github.com/yourusername/your-repo-name.git
```

### 2. Navigate to project

```
cd your-repo-name
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

### 4. Create .env file

```
MONGO_URI=your_mongodb_connection_string
SECRET_KEY=your_secret_key
```

### 5. Run the application

```
python app.py
```

Open browser:

```
http://127.0.0.1:5000
```

---

## Security Implemented

* Password hashing using bcrypt
* Login rate limiting
* CSRF protection
* Environment variables for secrets
* Session authentication
* Input validation

---

## Purpose of Project

This project was built to practice **backend development with Flask and MongoDB** and to understand how real-world web applications manage authentication, security, and database operations.

---

## Future Improvements

* REST API version of the system
* Role-based access control
* JWT authentication
* Docker deployment
* Logging and monitoring

---

## Author

Python Backend Developer
