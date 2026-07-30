from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "college_event_secret_key"

# ---------------- MongoDB Connection ----------------
client = MongoClient("mongodb+srv://mohankasimkota2124_db_user:Mohan12345@eventmanagement.4ty9aqy.mongodb.net/?appName=eventmanagement")

db = client["college_event_db"]

students = db["students"]
admins = db["admins"]
events = db["events"]
registrations = db["registrations"]
# ---------------- Home ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Admin Login
        if email == "admin@campusevents.com" and password == "Admin@123":
            session["admin"] = True
            return redirect("/admin")

        # Student Login
        student = students.find_one({
            "email": email,
            "password": password
        })

        if student:
            session["student"] = str(student["_id"])
            session["student_name"] = student["name"]
            return redirect("/student_dashboard")

        return "Invalid Email or Password!"

    return render_template("login.html")
from bson.objectid import ObjectId

@app.route("/student_dashboard")
def student_dashboard():

    if "student" not in session:
        return redirect("/login")

    page = request.args.get("page")

    # ---------- Dashboard ----------
    if page is None:
        return render_template(
            "student_dashboard.html",
            student_name=session["student_name"],
            page="dashboard"
        )

    # ---------- My Registrations ----------
    elif page == "registrations":

        my_events = list(
            registrations.find({
                "student_id": session["student"]
            })
        )

        return render_template(
            "student_dashboard.html",
            student_name=session["student_name"],
            page="registrations",
            registrations=my_events
        )

    # ---------- My Profile ----------
    elif page == "profile":

        student = students.find_one({
            "_id": ObjectId(session["student"])
        })

        return render_template(
            "student_dashboard.html",
            student_name=session["student_name"],
            page="profile",
            student=student
        )

    return redirect("/student_dashboard")

@app.route("/student_events")
def student_events():

    if "student" not in session:
        return redirect("/login")

    all_events = list(events.find())

    return render_template(
        "student_events.html",
        events=all_events
    )
@app.route("/register_event/<id>")
def register_event(id):

    if "student" not in session:
        return redirect("/login")

    # Student Details
    student = students.find_one({
        "_id": ObjectId(session["student"])
    })

    # Event Details
    event = events.find_one({
        "_id": ObjectId(id)
    })

    # Check Duplicate Registration
    already_registered = registrations.find_one({
        "student_id": str(student["_id"]),
        "event_name": event["event_name"]
    })

    if already_registered:
        return """
        <script>
        alert("You have already registered for this event!");
        window.location.href="/student_events";
        </script>
        """

    # Registration Data
    registration = {
        "student_id": str(student["_id"]),
        "name": student["name"],
        "roll_no": student["roll_no"],
        "branch": student["branch"],
        "year": student["year"],
        "gender": student["gender"],
        "email": student["email"],

        "event_name": event["event_name"],
        "category": event["category"],
        "date": event["date"],
        "venue": event["venue"]
    }

    registrations.insert_one(registration)

    return """
    <script>
    alert("Event Registered Successfully!");
    window.location.href="/student_events";
    </script>
    """  
@app.route("/admin")
def admin():

    if "admin" not in session:
        return redirect("/login")

    all_events = list(events.find())

    return render_template("admin.html", events=all_events)

@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match!"

        student = {
            "name": request.form["name"],
            "roll_no": request.form["roll_no"],
            "branch": request.form["branch"],
            "year": request.form["year"],
            "gender": request.form["gender"],
            "email": request.form["email"],
            "password": password
        }

        students.insert_one(student)

        return """
        <script>
        alert("Student Registration Successful! ✔️");
        window.location.href="/";
        </script>
        """

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/update_profile", methods=["POST"])
def update_profile():

    if "student" not in session:
        return redirect("/login")

    students.update_one(

        {"_id": ObjectId(session["student"])},

        {

            "$set":{

                "name":request.form["name"],
                "branch":request.form["branch"],
                "year":request.form["year"],
                "email":request.form["email"],
                "password":request.form["password"]

            }

        }

    )

    return """
    <script>
    alert("Profile Updated Successfully!");
    window.location.href="/student_dashboard?page=profile";
    </script>
    """

@app.route("/add_event", methods=["GET", "POST"])
def add_event():

    if request.method == "POST":

        event = {
            "event_name": request.form["event_name"],
            "category": request.form["category"],
            "date": request.form["date"],
            "venue": request.form["venue"],
            "seats": request.form["seats"],
            "description": request.form["description"]
        }

        events.insert_one(event)

        return redirect("/admin")

    return render_template("add_event.html")

@app.route("/registered_students")
def registered_students():

    if "admin" not in session:
        return redirect("/login")

    all_students = list(students.find())

    return render_template(
        "registered_students.html",
        students=all_students
    )


# ---------------- Delete Event ----------------
@app.route("/delete_event/<id>")
def delete_event(id):

    events.delete_one({"_id": ObjectId(id)})

    return redirect("/admin")

# ---------------- Delete Student ----------------
@app.route("/delete_student/<id>")
def delete_student(id):

    if "admin" not in session:
        return redirect("/login")

    students.delete_one({"_id": ObjectId(id)})

    return redirect("/registered_students")


# ---------------- Edit Event ----------------
@app.route("/edit_event/<id>", methods=["GET", "POST"])
def edit_event(id):

    if request.method == "POST":

        events.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "event_name": request.form["event_name"],
                    "category": request.form["category"],
                    "date": request.form["date"],
                    "venue": request.form["venue"],
                    "seats": request.form["seats"],
                    "description": request.form["description"]
                }
            }
        )

        return redirect("/admin")

    event = events.find_one({"_id": ObjectId(id)})

    return render_template("edit_event.html", event=event)

# ---------------- Test MongoDB ----------------
@app.route("/test")
def test():
    return {
        "message": "MongoDB Connected Successfully!",
        "students_collection": students.count_documents({}),
        "admins_collection": admins.count_documents({})
    }

if __name__ == "__main__":
    app.run(debug=True)