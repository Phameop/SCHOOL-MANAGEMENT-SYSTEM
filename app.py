from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "school_management_secret_key"

# ==========================
# DATABASE CONNECTION
# ==========================

conn = sqlite3.connect("school.db", check_same_thread=False)
cursor = conn.cursor()

# ==========================
# STUDENTS TABLE
# ==========================

# STUDENTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    roll TEXT,
    class_name TEXT
)
""")

# TEACHERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    subject TEXT,
    phone TEXT,
    email TEXT
)
""")

# ATTENDANCE TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    attendance_date TEXT,
    status TEXT
)
""")
# RESULTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    subject TEXT,
    marks INTEGER
)
""")


conn.commit()
# FEES TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    class_name TEXT,
    total_fee INTEGER,
    paid_fee INTEGER,
    remaining_fee INTEGER
)
""")

conn.commit()

# ==========================
# LOGIN CREDENTIALS
# ==========================

USERNAME = "admin"
PASSWORD = "admin123"

# ==========================
# LOGIN PAGE
# ==========================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == USERNAME and password == PASSWORD:

            session["logged_in"] = True

            return redirect("/dashboard")

        else:
            return render_template(
                "login.html",
                error="Invalid Username or Password"
            )

    return render_template("login.html")
# ==========================
# DASHBOARD
# ==========================

@app.route("/dashboard")
def dashboard():

    if "logged_in" not in session:
        return redirect("/")

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teachers")
    total_teachers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM results")
    total_results = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(remaining_fee) FROM fees")
    total_due = cursor.fetchone()[0]

    if total_due is None:
        total_due = 0

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_teachers=total_teachers,
        total_attendance=total_attendance,
        total_results=total_results,
        total_due=total_due
    )
# ==========================
# STUDENTS
# ==========================

@app.route("/students", methods=["GET", "POST"])
def students():

    if "logged_in" not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]
        student_class = request.form["student_class"]

        cursor.execute(
            "INSERT INTO students (name, roll, class_name) VALUES (?, ?, ?)",
            (name, roll, student_class)
        )

        conn.commit()

    search = request.args.get("search")

    if search:

        cursor.execute(
            """
            SELECT * FROM students
            WHERE name LIKE ?
            OR roll LIKE ?
            """,
            (f"%{search}%", f"%{search}%")
        )

    else:

        cursor.execute("SELECT * FROM students")

    students = cursor.fetchall()

    return render_template(
        "student.html",
        students=students
    
    )

# ==========================
# DELETE STUDENT
# ==========================

@app.route("/delete_student/<int:id>")
def delete_student(id):

    if "logged_in" not in session:
        return redirect("/")

    cursor.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()

    return redirect("/students")

# ==========================
# EDIT STUDENT
# ==========================

@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if "logged_in" not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]
        student_class = request.form["student_class"]

        cursor.execute(
            """
            UPDATE students
            SET name=?, roll=?, class_name=?
            WHERE id=?
            """,
            (name, roll, student_class, id)
        )

        conn.commit()

        return redirect("/students")

    cursor.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = cursor.fetchone()

    return render_template(
        "edit_student.html",
        student=student
    )

# ==========================
# TEACHERS
# ==========================

@app.route("/teachers", methods=["GET", "POST"])
def teachers():

    if "logged_in" not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form["name"]
        subject = request.form["subject"]
        phone = request.form["phone"]
        email = request.form["email"]

        cursor.execute(
            """
            INSERT INTO teachers
            (name, subject, phone, email)
            VALUES (?, ?, ?, ?)
            """,
            (name, subject, phone, email)
        )

        conn.commit()

    cursor.execute("SELECT * FROM teachers")
    teachers = cursor.fetchall()

    return render_template(
        "teachers.html",
        teachers=teachers
    )

# ==========================
# ATTENDANCE
# ==========================
@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    if "logged_in" not in session:
        return redirect("/")

    if request.method == "POST":

        student_name = request.form["student_name"]
        attendance_date = request.form["attendance_date"]
        status = request.form["status"]

        cursor.execute(
            """
            INSERT INTO attendance
            (student_name, attendance_date, status)
            VALUES (?, ?, ?)
            """,
            (student_name, attendance_date, status)
        )

        conn.commit()

    cursor.execute("SELECT * FROM attendance")

    attendance_data = cursor.fetchall()

    return render_template(
        "attendance.html",
        attendance=attendance_data
    )


# ==========================
# RESULTS
# ==========================
@app.route("/results", methods=["GET", "POST"])
def results():

    if "logged_in" not in session:
        return redirect("/")

    if request.method == "POST":

        student_name = request.form["student_name"]
        subject = request.form["subject"]
        marks = int(request.form["marks"])

        cursor.execute(
            """
            INSERT INTO results
            (student_name, subject, marks)
            VALUES (?, ?, ?)
            """,
            (student_name, subject, marks)
        )

        conn.commit()

    cursor.execute("SELECT * FROM results")

    results_data = cursor.fetchall()

    return render_template(
        "results.html",
        results=results_data
    )
conn.commit()

# ==========================
# FEES MANAGEMENT
# ==========================

@app.route("/fees", methods=["GET", "POST"])
def fees():

    if "logged_in" not in session:
        return redirect("/")

    if request.method == "POST":

        student_name = request.form["student_name"]
        class_name = request.form["class_name"]

        total_fee = int(request.form["total_fee"])
        paid_fee = int(request.form["paid_fee"])

        remaining_fee = total_fee - paid_fee

        cursor.execute(
            """
            INSERT INTO fees
            (
                student_name,
                class_name,
                total_fee,
                paid_fee,
                remaining_fee
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                student_name,
                class_name,
                total_fee,
                paid_fee,
                remaining_fee
            )
        )

        conn.commit()

    cursor.execute("SELECT * FROM fees")

    fees_data = cursor.fetchall()

    return render_template(
        "fees.html",
        fees=fees_data
    )
# ==========================
# log out
# ==========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


import webbrowser
from threading import Timer

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    Timer(1, open_browser).start()
    app.run(debug=False)