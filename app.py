from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# ---------------- MYSQL CONFIG ---------------- #

app.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST", "localhost")
app.config['MYSQL_PORT'] = int(os.environ.get("MYSQL_PORT", 3306))
app.config['MYSQL_USER'] = os.environ.get("MYSQL_USER", "root")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD", "")
app.config['MYSQL_DB'] = os.environ.get("MYSQL_DB", "college_event")

mysql = MySQL(app)

# ---------------- HOME ---------------- #

@app.route('/')
def home():
    if 'id' in session:
        if session['role'] == "Admin":
            return redirect('/admin')
        return redirect('/student')
    return redirect('/login')

# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        account = cur.fetchone()

        if account:
            flash("Email already exists!", "danger")
            return redirect('/register')

        cur.execute("""
INSERT INTO events(title,description,event_date,event_time,venue)
VALUES(%s,%s,%s,%s,%s)
""", (title, description, event_date, event_time, venue))

        flash("Registration Successful!", "success")
        return redirect('/login')

    return render_template("register.html")
# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,)
        )

        user = cur.fetchone()
        cur.close()

        if user:

            # users table order:
            # id | name | email | password | role

            if check_password_hash(user[3], password):

                session['id'] = user[0]
                session['name'] = user[1]
                session['email'] = user[2]
                session['role'] = user[4]

                flash("Login Successful!", "success")

                if user[4] == "Admin":
                    return redirect('/admin')
                else:
                    return redirect('/student')

            else:
                flash("Incorrect Password!", "danger")

        else:
            flash("Email not found!", "danger")

    return render_template("login.html")


# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():

    session.clear()

    flash("Logged out successfully!", "success")

    return redirect('/login')
# ---------------- ADMIN DASHBOARD ---------------- #

@app.route('/admin')
def admin():

    if 'id' not in session or session['role'] != 'Admin':
        return redirect('/login')

    cur = mysql.connection.cursor()

    # Total Students
    cur.execute("SELECT COUNT(*) FROM users WHERE role='Student'")
    total_students = cur.fetchone()[0]

    # Total Events
    cur.execute("SELECT COUNT(*) FROM events")
    total_events = cur.fetchone()[0]

    # Total Registrations
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

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():

    if 'id' not in session or session['role'] != 'Admin':
        return redirect('/login')

    if request.method == 'POST':

        title = request.form['title']
        description = request.form['description']
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        venue = request.form['venue']

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO events(title, description, event_date, venue)
            VALUES(%s,%s,%s,%s)
        """, (title, description, event_date, venue))

        mysql.connection.commit()
        cur.close()

        flash("Event Added Successfully!", "success")
        return redirect('/view_events')

    return render_template("add_event.html")


# ---------------- VIEW EVENTS ---------------- #

@app.route('/view_events')
def view_events():

    if 'id' not in session or session['role'] != 'Admin':
        return redirect('/login')

    search = request.args.get('search', '')

    cur = mysql.connection.cursor()

    if search:
        cur.execute("""
            SELECT * FROM events
            WHERE title LIKE %s
            ORDER BY event_date ASC
        """, ('%' + search + '%',))
    else:
        cur.execute("""
            SELECT * FROM events
            ORDER BY event_date ASC
        """)

    events = cur.fetchall()

    cur.close()

    return render_template(
        "view_events.html",
        events=events,
        search=search
    )


# ---------------- DELETE EVENT ---------------- #

@app.route('/delete_event/<int:id>')
def delete_event(id):

    if 'id' not in session or session['role'] != 'Admin':
        return redirect('/login')

    cur = mysql.connection.cursor()

    # Delete registrations first
    cur.execute("DELETE FROM registrations WHERE event_id=%s", (id,))

    # Delete event
    cur.execute("DELETE FROM events WHERE id=%s", (id,))

    mysql.connection.commit()

    cur.close()

    flash("Event Deleted Successfully!", "success")

    return redirect('/view_events')


# ---------------- REGISTERED STUDENTS ---------------- #

@app.route('/registered_students/<int:event_id>')
def registered_students(event_id):

    if 'id' not in session or session['role'] != 'Admin':
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT users.name,
               users.email,
               registrations.registered_at
        FROM registrations
        JOIN users
            ON registrations.student_id = users.id
        WHERE registrations.event_id=%s
        ORDER BY registrations.registered_at DESC
    """, (event_id,))

    students = cur.fetchall()

    cur.close()

    return render_template(
        "registered_students.html",
        students=students
    )
# ---------------- STUDENT DASHBOARD ---------------- #

@app.route('/student')
def student():

    if 'id' not in session or session['role'] != 'Student':
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM events")
    total_events = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM registrations WHERE student_id=%s",
        (session['id'],)
    )
    my_events = cur.fetchone()[0]

    cur.close()

    return render_template(
        "student.html",
        total_events=total_events,
        my_events=my_events
    )


# ---------------- STUDENT VIEW EVENTS ---------------- #

@app.route('/student_events')
def student_events():

    if 'id' not in session or session['role'] != 'Student':
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT * FROM events
        ORDER BY event_date ASC
    """)

    events = cur.fetchall()

    cur.close()

    return render_template("student_events.html", events=events)


# ---------------- REGISTER EVENT ---------------- #

@app.route('/register_event/<int:event_id>')
def register_event(event_id):

    if 'id' not in session or session['role'] != 'Student':
        return redirect('/login')

    cur = mysql.connection.cursor()

    # Check already registered
    cur.execute("""
        SELECT * FROM registrations
        WHERE student_id=%s AND event_id=%s
    """, (session['id'], event_id))

    already = cur.fetchone()

    if already:
        flash("You have already registered for this event!", "warning")
        cur.close()
        return redirect('/student_events')

    cur.execute("""
        INSERT INTO registrations(student_id,event_id)
        VALUES(%s,%s)
    """, (session['id'], event_id))

    mysql.connection.commit()

    cur.close()

    flash("Event Registered Successfully!", "success")

    return redirect('/student_events')


# ---------------- MY REGISTRATIONS ---------------- #

@app.route('/my_registrations')
def my_registrations():

    if 'id' not in session or session['role'] != 'Student':
        return redirect('/login')

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT events.title,
               events.event_date,
               events.venue,
               registrations.registered_at
        FROM registrations
        JOIN events
        ON registrations.event_id = events.id
        WHERE registrations.student_id=%s
        ORDER BY events.event_date ASC
    """, (session['id'],))

    registrations = cur.fetchall()

    cur.close()

    return render_template(
        "my_registrations.html",
        registrations=registrations
    )
# ---------------- FORGOT PASSWORD ---------------- #

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        email = request.form['email']
        new_password = generate_password_hash(request.form['new_password'])

        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if user:

            cur.execute(
                "UPDATE users SET password=%s WHERE email=%s",
                (new_password, email)
            )

            mysql.connection.commit()
            flash("Password Updated Successfully! Please Login.", "success")

            cur.close()
            return redirect('/login')

        flash("Email not found!", "danger")
        cur.close()

    return render_template("forgot_password.html")


# ---------------- ERROR PAGES ---------------- #

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":
    app.run(debug=True)