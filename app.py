from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from datetime import datetime, date 
import os
app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "college_event_secret")

# ---------------- MYSQL CONFIG ---------------- #

app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "localhost")
app.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT", 3306))
app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "root")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "")
app.config["MYSQL_DB"] = os.environ.get("MYSQL_DB", "college_event")

app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return redirect(url_for("login"))

# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])
        role = "Student"

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT id FROM users WHERE email=%s",
            (email,)
        )

        account = cur.fetchone()

        if account:
            flash("Email already exists!", "danger")
            cur.close()
            return redirect(url_for("register"))

        cur.execute("""
            INSERT INTO users
            (name,email,password,role)
            VALUES(%s,%s,%s,%s)
        """,(name,email,password,role))

        mysql.connection.commit()

        cur.close()

        flash("Registration Successful!", "success")

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method=="POST":

        email=request.form["email"]
        password=request.form["password"]

        cur=mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user=cur.fetchone()

        cur.close()

        if user:

            if check_password_hash(user[3],password):

                session["id"]=user[0]
                session["name"]=user[1]
                session["email"]=user[2]
                session["role"]=user[4]

                flash("Login Successful","success")

                if user[4]=="Admin":
                    return redirect(url_for("admin_dashboard"))

                return redirect(url_for("student_dashboard"))

        flash("Invalid Email or Password","danger")

    return render_template("login.html")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully","success")

    return redirect(url_for("login"))
# ---------------- FORGOT PASSWORD ---------------- #

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]
        new_password = generate_password_hash(request.form["password"])

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cur.fetchone()

        if user:

            cur.execute(
                "UPDATE users SET password=%s WHERE email=%s",
                (new_password, email)
            )

            mysql.connection.commit()

            cur.close()

            flash("Password Updated Successfully!", "success")

            return redirect(url_for("login"))

        else:

            cur.close()

            flash("Email Not Found!", "danger")

    return render_template("forgot_password.html")
# ---------------- ADMIN DASHBOARD ---------------- #

@app.route("/admin")
def admin_dashboard():

    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM users WHERE role='Student'")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM events")
    total_events = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM registrations")
    total_registrations = cur.fetchone()[0]

    cur.close()

    return render_template(
        "admin.html",
        total_students=total_students,
        total_events=total_events,
        total_registrations=total_registrations
    )


# ---------------- ADD EVENT ---------------- #

@app.route("/add_event", methods=["GET", "POST"])
def add_event():

    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        event_date = request.form["event_date"]
        event_time = request.form['event_time']
        venue = request.form["venue"]

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO events
            (title,description,event_date,venue)
            VALUES(%s,%s,%s,%s)
        """,
        (title, description, event_date, venue))

        mysql.connection.commit()

        cur.close()

        flash("Event Added Successfully!", "success")

        return redirect(url_for("view_events"))

    return render_template("add_event.html")


# ---------------- VIEW EVENTS ---------------- #

@app.route("/view_events")
def view_events():

    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM events
        ORDER BY event_date ASC
    """)

    events = cur.fetchall()

    cur.close()

    return render_template(
        "view_events.html",
        events=events
    )


# ---------------- DELETE EVENT ---------------- #

@app.route("/delete_event/<int:event_id>")
def delete_event(event_id):

    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    # Delete registrations first
    cur.execute(
        "DELETE FROM registrations WHERE event_id=%s",
        (event_id,)
    )

    # Delete event
    cur.execute(
        "DELETE FROM events WHERE id=%s",
        (event_id,)
    )

    mysql.connection.commit()

    cur.close()

    flash("Event Deleted Successfully!", "success")

    return redirect(url_for("view_events"))
# ---------------- EDIT EVENT ---------------- #

@app.route("/edit_event/<int:event_id>", methods=["GET", "POST"])
def edit_event(event_id):

    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        event_date = request.form["event_date"]
        venue = request.form["venue"]

        cur.execute("""
            UPDATE events
            SET
                title=%s,
                description=%s,
                event_date=%s,
                venue=%s
            WHERE id=%s
        """, (title, description, event_date, venue, event_id))

        mysql.connection.commit()

        cur.close()

        flash("Event Updated Successfully!", "success")

        return redirect(url_for("view_events"))

    cur.execute("SELECT * FROM events WHERE id=%s", (event_id,))
    event = cur.fetchone()

    cur.close()

    return render_template("edit_event.html", event=event)

# ---------------- REGISTERED STUDENTS ---------------- #

@app.route("/registered_students")
def registered_students():

    if "id" not in session or session["role"] != "Admin":
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            r.id,
            u.name,
            u.email,
            e.title,
            r.roll_no,
            r.branch,
            r.year,
            r.gender,
            r.phone,
            r.registered_at
        FROM registrations r
        JOIN users u
            ON r.student_id = u.id
        JOIN events e
            ON r.event_id = e.id
        ORDER BY r.registered_at DESC
    """)

    students = cur.fetchall()

    cur.close()

    return render_template(
        "registered_students.html",
        students=students
    )
# ---------------- STUDENT DASHBOARD ---------------- #

@app.route("/student")
def student_dashboard():

    if "id" not in session or session["role"] != "Student":
        return redirect(url_for("login"))

    return render_template("student.html")


# ---------------- STUDENT EVENTS ---------------- #
@app.route("/student_events")
def student_events():

    if "id" not in session or session["role"] != "Student":
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT *
        FROM events
        ORDER BY event_date ASC
    """)

    events = cur.fetchall()

    cur.close()

    return render_template(
        "student_events.html",
        events=events,
        today=date.today()
    )


# ---------------- REGISTER EVENT ---------------- #
@app.route("/register_event/<int:event_id>", methods=["GET", "POST"])
def register_event(event_id):

    if "id" not in session or session["role"] != "Student":
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    # Get Event
    cur.execute("SELECT * FROM events WHERE id=%s", (event_id,))
    event = cur.fetchone()

    if not event:
        flash("Event not found!", "danger")
        cur.close()
        return redirect(url_for("student_events"))

    # Check event date
    if event[3] < date.today():
        flash("Registration Link Expired!", "danger")
        cur.close()
        return redirect(url_for("student_events"))

    # Already Registered?
    cur.execute("""
        SELECT id
        FROM registrations
        WHERE student_id=%s
        AND event_id=%s
    """, (session["id"], event_id))

    already = cur.fetchone()

    if already:
        cur.close()
        flash("You have already registered for this event!", "warning")
        return redirect(url_for("student_events"))

    if request.method == "POST":

        roll_no = request.form["roll_no"]
        branch = request.form["branch"]
        year = request.form["year"]
        gender = request.form["gender"]
        phone = request.form["phone"]

        cur.execute("""
            INSERT INTO registrations
            (
                student_id,
                event_id,
                roll_no,
                branch,
                year,
                gender,
                phone
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            session["id"],
            event_id,
            roll_no,
            branch,
            year,
            gender,
            phone
        ))

        mysql.connection.commit()

        cur.close()

        flash("Event Registered Successfully!", "success")

        return redirect(url_for("my_registrations"))

    cur.close()

    return render_template(
        "student_event_register.html",
        event_id=event_id
    )


# ---------------- MY REGISTRATIONS ---------------- #

@app.route("/my_registrations")
def my_registrations():

    if "id" not in session or session["role"] != "Student":
        return redirect(url_for("login"))

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            e.title,
            e.description,
            e.event_date,
            e.venue,
            r.registered_at
        FROM registrations r
        JOIN events e
        ON r.event_id = e.id
        WHERE r.student_id=%s
        ORDER BY r.registered_at DESC
    """, (session["id"],))

    registrations = cur.fetchall()

    cur.close()

    return render_template(
        "my_registrations.html",
        registrations=registrations
    )


# ---------------- ERROR PAGES ---------------- #

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


# ---------------- MAIN ---------------- #

if __name__ == "__main__":
    app.run(debug=True)