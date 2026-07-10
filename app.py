from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import config

app = Flask(__name__)

# ---------------- SECRET KEY ---------------- #

app.secret_key = config.SECRET_KEY

# ---------------- MYSQL CONFIG ---------------- #

app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL(app)


# ---------------- HOME ---------------- #

@app.route('/')
def home():

    if 'id' in session:

        if session['role'] == "Admin":
            return redirect('/admin')
        else:
            return redirect('/student')

    return redirect('/login')


# ---------------- REGISTER ---------------- #

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == "POST":

        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        # Student accounts only from registration page
        role = "Student"

        if not name or not email or not password:
            flash("All fields are required")
            return redirect('/register')

        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT id FROM users WHERE email=%s",
            (email,)
        )

        existing = cur.fetchone()

        if existing:
            cur.close()
            flash("Email already registered")
            return redirect('/register')

        cur.execute(
            """
            INSERT INTO users
            (name,email,password,role)
            VALUES(%s,%s,%s,%s)
            """,
            (
                name,
                email,
                hashed_password,
                role
            )
        )

        mysql.connection.commit()
        cur.close()

        flash("Registration Successful")
        return redirect('/login')

    return render_template("register.html")


# ---------------- LOGIN ---------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":

        email = request.form['email'].strip().lower()
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            """
            SELECT id,name,email,password,role
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cur.fetchone()

        cur.close()

        if user:

            if check_password_hash(user[3], password):

                session['id'] = user[0]
                session['name'] = user[1]
                session['role'] = user[4]

                flash("Login Successful")

                if user[4] == "Admin":
                    return redirect('/admin')

                return redirect('/student')

        flash("Invalid Email or Password")

    return render_template("login.html")
# ---------------- ADMIN DASHBOARD ---------------- #

@app.route('/admin')
def admin():

    if 'id' not in session:
        return redirect('/login')

    if session['role'] != "Admin":
        flash("Access Denied")
        return redirect('/student')

    cur = mysql.connection.cursor()

    cur.execute("SELECT COUNT(*) FROM events")
    total_events = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM users WHERE role='Student'")
    total_students = cur.fetchone()[0]

    cur.close()

    return render_template(
        "admin.html",
        total_events=total_events,
        total_students=total_students
    )


# ---------------- STUDENT DASHBOARD ---------------- #

@app.route('/student')
def student():

    if 'id' not in session:
        return redirect('/login')

    if session['role'] != "Student":
        return redirect('/admin')

    return render_template(
        "student.html"
    )


# ---------------- ADD EVENT ---------------- #

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():

    if 'id' not in session:
        return redirect('/login')

    if session['role'] != "Admin":
        flash("Access Denied")
        return redirect('/student')

    if request.method == "POST":

        title = request.form['title']
        description = request.form['description']
        event_date = request.form['event_date']
        event_time = request.form['event_time']
        venue = request.form['venue']
        category = request.form['category']
        registration_deadline = request.form['registration_deadline']

        cur = mysql.connection.cursor()

        cur.execute("""
            INSERT INTO events
            (
                title,
                description,
                event_date,
                event_time,
                venue,
                category,
                registration_deadline
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            title,
            description,
            event_date,
            event_time,
            venue,
            category,
            registration_deadline
        ))

        mysql.connection.commit()
        cur.close()

        flash("Event Added Successfully")

        return redirect('/view_events')

    return render_template(
        "add_event.html"
    )


# ---------------- VIEW EVENTS ---------------- #

@app.route('/view_events')
def view_events():

    if 'id' not in session:
        return redirect('/login')

    if session['role'] != "Admin":
        flash("Access Denied")
        return redirect('/student')

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
# ---------------- STUDENT VIEW EVENTS ---------------- #

@app.route('/student_events')
def student_events():

    if 'id' not in session:
        return redirect('/login')

    if session['role'] != "Student":
        return redirect('/admin')

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
        events=events
    )


# ---------------- REGISTER EVENT ---------------- #

@app.route('/register_event/<int:event_id>', methods=['GET', 'POST'])
def register_event(event_id):

    if 'id' not in session:
        return redirect('/login')

    if session['role'] != "Student":
        return redirect('/admin')

    user_id = session['id']

    cur = mysql.connection.cursor()

    # Get Event Details
    cur.execute(
        "SELECT * FROM events WHERE id=%s",
        (event_id,)
    )

    event = cur.fetchone()

    if not event:
        cur.close()
        flash("Event not found")
        return redirect('/student_events')

    if request.method == "POST":

        student_name = request.form['student_name']
        roll_no = request.form['roll_no']
        email = request.form['email']
        mobile = request.form['mobile']
        student_class = request.form['student_class']
        branch = request.form['branch']
        gender = request.form['gender']

        # Check Duplicate Registration
        cur.execute(
            """
            SELECT id
            FROM registrations
            WHERE user_id=%s
            AND event_id=%s
            """,
            (user_id, event_id)
        )

        existing = cur.fetchone()

        if existing:
            cur.close()
            flash("You have already registered for this event.")
            return redirect('/student_events')

        cur.execute("""
            INSERT INTO registrations
            (
                user_id,
                event_id,
                student_name,
                roll_no,
                email,
                mobile,
                class,
                branch,
                gender
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            user_id,
            event_id,
            student_name,
            roll_no,
            email,
            mobile,
            student_class,
            branch,
            gender
        ))

        mysql.connection.commit()

        cur.close()

        flash("Event Registered Successfully")

        return redirect('/my_registrations')

    cur.close()

    return render_template(
        "register_event.html",
        event=event
    )


# ---------------- MY REGISTRATIONS ---------------- #

# ---------------- MY REGISTRATIONS ---------------- #

@app.route('/my_registrations')
def my_registrations():

    if 'id' not in session:
        return redirect('/login')

    if session['role'] != "Student":
        return redirect('/admin')

    user_id = session['id']

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT 
            events.title,
            events.description,
            events.event_date,
            events.event_time,
            events.venue,
            events.category
        FROM registrations
        INNER JOIN events
        ON registrations.event_id = events.id
        WHERE registrations.user_id=%s
    """, (user_id,))

    registrations = cur.fetchall()

    cur.close()

    print("MY REGISTRATIONS:", registrations)

    return render_template(
        "my_registrations.html",
        registrations=registrations
    )
# ---------------- REGISTERED STUDENTS ---------------- #

@app.route('/registered_students')
def registered_students():

    if 'id' not in session:
        return redirect('/login')

    if session['role'] != "Admin":
        flash("Access Denied")
        return redirect('/student')

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT
            users.name,
            users.email,
            events.title,
            events.event_date,
            events.venue
        FROM registrations

        INNER JOIN users
        ON registrations.user_id = users.id

        INNER JOIN events
        ON registrations.event_id = events.id

        ORDER BY events.event_date ASC
    """)

    students = cur.fetchall()

    cur.close()

    return render_template(
        "registered_students.html",
        students=students
    )


# ---------------- LOGOUT ---------------- #

@app.route('/logout')
def logout():

    session.clear()

    flash("Logged out successfully")

    return redirect('/login')


# ---------------- RUN APP ---------------- #

if __name__ == "__main__":

    app.run(debug=True)