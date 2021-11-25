from flask import (
    Flask,
    redirect,
    url_for,
    render_template,
    request,
    session,
    redirect,
    url_for,
    g,
    jsonify,
)

from datetime import timedelta

import jyserver.Flask as jsf

from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)
app.secret_key = "239ksaliSnYa6c01anLAn235herE10"

app.permanent_session_lifetime = timedelta(days=365)


# Configure Database
db = yaml.load(open("db.yaml"))
app.config["MYSQL_HOST"] = db["mysql_host"]
app.config["MYSQL_USER"] = db["mysql_user"]
app.config["MYSQL_PASSWORD"] = db["mysql_password"]
app.config["MYSQL_DB"] = db["mysql_db"]

mysql = MySQL(app)


def calculate_gradepoint(table_name):
    cursor = mysql.connection.cursor()
    resultValue = cursor.execute(
        "SELECT grade_point, credit FROM " + table_name + " WHERE username='rafid'"
    )
    courseDetails = cursor.fetchall()
    cursor.close()

    sum = 0

    for courseInfo in courseDetails:
        try:
            sum += float(courseInfo[0]) * float(courseInfo[1])
        except Exception:
            return 0

    return sum


def get_credit(table_name):
    cursor = mysql.connection.cursor()
    resultValue = cursor.execute(
        "SELECT SUM(credit) FROM " + table_name + " WHERE username='rafid'"
    )
    creditDetails = cursor.fetchall()
    cursor.close()

    for sumCredit in creditDetails:
        try:
            return float(sumCredit[0])
        except Exception:
            return 0


@app.route("/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        # Fetch the form data
        if request.form["loginform"] == "yes":
            email = request.form["email"]
            password = request.form["password"]

            cursor = mysql.connection.cursor()

            resultValue = cursor.execute(
                "SELECT username, email, password FROM student WHERE email=%s",
                (email,),
            )

            row = cursor.fetchone()
            cursor.close()

            if row != None:
                if row[2] == password:
                    session["user"] = row[0]
                    return redirect(url_for("my_course"))

            else:
                return "<h1>Not Found</h1>"

        elif request.form["loginform"] == "no":
            username = request.form["username"]
            email = request.form["email"]
            university_name = request.form["university_name"]
            password = request.form["password"]

            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO student VALUES (%s, %s, %s, %s)",
                (username, email, university_name, password),
            )
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for("login"))

    else:
        if "user" in session:
            return redirect(url_for("my_course"))

        cursor = mysql.connection.cursor()
        resultValue = cursor.execute("SELECT university_name FROM university")
        universityName = cursor.fetchall()
        return render_template("login.html", universityName=universityName)


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":

        # Fetch the form data

        username = request.form["username"]
        email = request.form["email"]
        university_name = request.form["university_name"]
        password = request.form["password"]

        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO student VALUES (%s, %s, %s, %s)",
            (username, email, university_name, password),
        )
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for("login"))

    else:

        if "user" in session:
            return redirect(url_for("my_course"))

        cursor = mysql.connection.cursor()
        resultValue = cursor.execute("SELECT university_name FROM university")
        universityName = cursor.fetchall()
        return render_template("registration.html", universityName=universityName)


@app.route("/mycourses", methods=["POST", "GET"])
def my_course():

    if "user" in session:

        user = session["user"]

        if request.method == "POST":

            action = request.form["action"]

            # If the post action is adding course or editing course
            if action == "add-course" or action == "edit-course":

                # Gathering info from ajax post request data
                course_init = request.form["course_init"]
                grade = request.form["grade"]
                total_marks = request.form["total_marks"]
                credit = request.form["credit"]

                # If user only pass the total mark
                if total_marks and not grade:
                    cursor = mysql.connection.cursor()
                    resultValue = cursor.execute(
                        "SELECT * FROM grading_policy WHERE grading_policy_id = 1"
                    )
                    grading_policy = cursor.fetchall()
                    for grade_num in grading_policy:
                        i = 1
                        while i <= 23:
                            if grade_num[i]:
                                if grade_num[i] >= round(
                                    float(total_marks)
                                ) and grade_num[i + 1] <= round(float(total_marks)):
                                    # grade_marks = grade_num[i]
                                    store_index = i
                                    cursor.close()
                                    if store_index == 1:
                                        grade_marks = "A+"
                                    elif store_index == 3:
                                        grade_marks = "A"
                                    elif store_index == 5:
                                        grade_marks = "A-"
                                    elif store_index == 7:
                                        grade_marks = "B+"
                                    elif store_index == 9:
                                        grade_marks = "B"
                                    elif store_index == 11:
                                        grade_marks = "B-"
                                    elif store_index == 13:
                                        grade_marks = "C+"
                                    elif store_index == 15:
                                        grade_marks = "C"
                                    elif store_index == 17:
                                        grade_marks = "C-"
                                    elif store_index == 19:
                                        grade_marks = "D+"
                                    elif store_index == 21:
                                        grade_marks = "D"
                                    elif store_index == 23:
                                        grade_marks = "F"

                                    cursor = mysql.connection.cursor()

                                    # Collecting grade point of that specific grade from database
                                    resultValue = cursor.execute(
                                        "SELECT grade_point FROM grade_point_policy WHERE grade = %s and grading_policy_id = (SELECT grading_policy_id FROM university WHERE university_name = (SELECT university_name from STUDENT where username=%s));",
                                        (
                                            grade_marks,
                                            user,
                                        ),
                                    )

                                    grade_point_policy = cursor.fetchall()

                                    for grade_points in grade_point_policy:
                                        grade_point = str(grade_points[0])

                                    cursor.close()

                                    # If adding course, it will only add that course in database
                                    if action == "add-course":
                                        # Storing in database
                                        cursor = mysql.connection.cursor()
                                        cursor.execute(
                                            "INSERT INTO course_info VALUES (%s, %s, %s, %s, %s)",
                                            (
                                                user,
                                                course_init,
                                                grade_marks,
                                                grade_point,
                                                credit,
                                            ),
                                        )
                                        mysql.connection.commit()
                                        cursor.close()

                                        sumGradePoint = calculate_gradepoint(
                                            "course_info"
                                        )
                                        sumCredit = get_credit("course_info")

                                        # cgpa = sumGradePoint / sumCredit
                                        try:
                                            cgpa = sumGradePoint / sumCredit
                                        except Exception:
                                            cgpa = 0

                                        return jsonify(
                                            {
                                                "grade_marks": grade_marks,
                                                "grade_point": grade_point,
                                                "cgpa": round(cgpa, 2),
                                                "creditPassed": sumCredit,
                                            }
                                        )

                                    # If editing course, it will update that course in database
                                    elif action == "edit-course":

                                        prev_course_init = request.form[
                                            "prev_course_init"
                                        ]
                                        prev_grade = request.form["prev_grade"]
                                        prev_grade_point = request.form[
                                            "prev_grade_point"
                                        ]
                                        prev_credit = request.form["prev_credit"]

                                        # Storing in database
                                        cursor = mysql.connection.cursor()
                                        cursor.execute(
                                            "UPDATE course_info SET course_init=%s, grade=%s, grade_point=%s, credit=%s WHERE username=%s and course_init=%s and grade=%s and grade_point=%s and credit=%s",
                                            (
                                                course_init,
                                                grade_marks,
                                                grade_point,
                                                credit,
                                                user,
                                                prev_course_init,
                                                prev_grade,
                                                prev_grade_point,
                                                prev_credit,
                                            ),
                                        )
                                        mysql.connection.commit()
                                        cursor.close()

                                        sumGradePoint = calculate_gradepoint(
                                            "course_info"
                                        )
                                        sumCredit = get_credit("course_info")

                                        # cgpa = sumGradePoint / sumCredit
                                        try:
                                            cgpa = sumGradePoint / sumCredit
                                        except Exception:
                                            cgpa = 0

                                        return jsonify(
                                            {
                                                "grade_marks": grade_marks,
                                                "grade_point": grade_point,
                                                "cgpa": round(cgpa, 2),
                                                "creditPassed": sumCredit,
                                            }
                                        )

                                i += 2

                            else:

                                i += 2

                # If someone passes grade as input, it will have more prio than total_marks
                elif grade:
                    grade_marks = str(grade)

                    cursor = mysql.connection.cursor()

                    resultValue = cursor.execute(
                        "SELECT grade_point FROM grade_point_policy WHERE grade = %s and grading_policy_id = (SELECT grading_policy_id FROM university WHERE university_name = (SELECT university_name from STUDENT where username=%s));",
                        (
                            grade_marks,
                            user,
                        ),
                    )

                    grade_point_policy = cursor.fetchall()

                    for grade_points in grade_point_policy:
                        grade_point = str(grade_points[0])

                    cursor.close()

                    if action == "add-course":
                        # Storing in database
                        cursor = mysql.connection.cursor()
                        cursor.execute(
                            "INSERT INTO course_info VALUES (%s, %s, %s, %s, %s)",
                            (user, course_init, grade_marks, grade_point, credit),
                        )
                        mysql.connection.commit()
                        cursor.close()

                        sumGradePoint = calculate_gradepoint("course_info")
                        sumCredit = get_credit("course_info")

                        # cgpa = sumGradePoint / sumCredit
                        try:
                            cgpa = sumGradePoint / sumCredit
                        except Exception:
                            cgpa = 0

                        return jsonify(
                            {
                                "grade_marks": grade_marks,
                                "grade_point": grade_point,
                                "cgpa": round(cgpa, 2),
                                "creditPassed": sumCredit,
                            }
                        )

                    elif action == "edit-course":

                        prev_course_init = request.form["prev_course_init"]
                        prev_grade = request.form["prev_grade"]
                        prev_grade_point = request.form["prev_grade_point"]
                        prev_credit = request.form["prev_credit"]

                        # Storing in database
                        cursor = mysql.connection.cursor()
                        cursor.execute(
                            "UPDATE course_info SET course_init=%s, grade=%s, grade_point=%s, credit=%s WHERE username=%s and course_init=%s and grade=%s and grade_point=%s and credit=%s",
                            (
                                course_init,
                                grade_marks,
                                grade_point,
                                credit,
                                user,
                                prev_course_init,
                                prev_grade,
                                prev_grade_point,
                                prev_credit,
                            ),
                        )
                        mysql.connection.commit()
                        cursor.close()

                        sumGradePoint = calculate_gradepoint("course_info")
                        sumCredit = get_credit("course_info")

                        # cgpa = sumGradePoint / sumCredit
                        try:
                            cgpa = sumGradePoint / sumCredit
                        except Exception:
                            cgpa = 0

                        return jsonify(
                            {
                                "grade_marks": grade_marks,
                                "grade_point": grade_point,
                                "cgpa": round(cgpa, 2),
                                "creditPassed": sumCredit,
                            }
                        )

            # DELETE ACTION
            elif action == "delete":
                course_init = request.form["course_init"]
                grade = request.form["grade"]
                grade_point = request.form["grade_point"]
                credit = request.form["credit"]

                cursor = mysql.connection.cursor()
                cursor.execute(
                    "DELETE FROM course_info WHERE username = %s and course_init = %s and grade = %s and grade_point = %s and credit = %s",
                    (user, course_init, grade, grade_point, credit),
                )
                mysql.connection.commit()
                cursor.close()

                sumGradePoint = calculate_gradepoint("course_info")
                sumCredit = get_credit("course_info")

                # cgpa = sumGradePoint / sumCredit

                try:
                    cgpa = sumGradePoint / sumCredit
                except Exception:
                    cgpa = 0

                return jsonify(
                    {"Status": "OK", "cgpa": round(cgpa, 2), "creditPassed": sumCredit}
                )

            elif action == "move-retake-course":

                course_init = request.form["course_init"]
                grade = request.form["grade"]
                grade_point = request.form["grade_point"]
                credit = request.form["credit"]

                cursor = mysql.connection.cursor()
                cursor.execute(
                    "INSERT INTO `retake_output` SELECT * FROM course_info WHERE username=%s and course_init = %s and grade = %s and grade_point = %s and credit = %s",
                    (user, course_init, grade, grade_point, credit),
                )
                cursor.execute(
                    "DELETE FROM course_info WHERE username=%s and course_init = %s and grade = %s and grade_point = %s and credit = %s",
                    (user, course_init, grade, grade_point, credit),
                )
                mysql.connection.commit()
                cursor.close()

                sumGradePoint = calculate_gradepoint("course_info")
                sumCredit = get_credit("course_info")

                # cgpa = sumGradePoint /
                try:
                    cgpa = sumGradePoint / sumCredit
                except Exception:
                    cgpa = 0

                return jsonify(
                    {"Status": "OK", "cgpa": round(cgpa, 2), "creditPassed": sumCredit}
                )

            return jsonify({"error": "Something went wrong!"})

        else:
            cursor = mysql.connection.cursor()
            resultValue = cursor.execute("SELECT * FROM course_info")
            courseDetails = cursor.fetchall()
            cursor.close()

            sumGradePoint = calculate_gradepoint("course_info")
            sumCredit = get_credit("course_info")

            # cgpa = sumGradePoint /
            try:
                cgpa = sumGradePoint / sumCredit
            except Exception:
                cgpa = 0

            return render_template(
                "myCourse.html",
                courseDetails=courseDetails,
                cgpa=round(cgpa, 2),
                creditPassed=sumCredit,
            )
    else:
        return redirect(url_for("login"))


@app.route("/prediction", methods=["POST", "GET"])
def grade_prediction():
    if "user" in session:

        user = session["user"]

        if request.method == "POST":

            action = request.form["action"]

            # If the post action is adding course or editing course
            if action == "add-course" or action == "edit-course":

                # Gathering info from ajax post request data
                course_init = request.form["course_init"]
                grade = request.form["grade"]
                total_marks = request.form["total_marks"]
                credit = request.form["credit"]

                # If user only pass the total mark
                if total_marks and not grade:
                    cursor = mysql.connection.cursor()
                    resultValue = cursor.execute(
                        "SELECT * FROM grading_policy WHERE grading_policy_id = 1"
                    )
                    grading_policy = cursor.fetchall()
                    for grade_num in grading_policy:
                        i = 1
                        while i <= 23:
                            if grade_num[i]:
                                if grade_num[i] >= round(
                                    float(total_marks)
                                ) and grade_num[i + 1] <= round(float(total_marks)):
                                    # grade_marks = grade_num[i]
                                    store_index = i
                                    cursor.close()
                                    if store_index == 1:
                                        grade_marks = "A+"
                                    elif store_index == 3:
                                        grade_marks = "A"
                                    elif store_index == 5:
                                        grade_marks = "A-"
                                    elif store_index == 7:
                                        grade_marks = "B+"
                                    elif store_index == 9:
                                        grade_marks = "B"
                                    elif store_index == 11:
                                        grade_marks = "B-"
                                    elif store_index == 13:
                                        grade_marks = "C+"
                                    elif store_index == 15:
                                        grade_marks = "C"
                                    elif store_index == 17:
                                        grade_marks = "C-"
                                    elif store_index == 19:
                                        grade_marks = "D+"
                                    elif store_index == 21:
                                        grade_marks = "D"
                                    elif store_index == 23:
                                        grade_marks = "F"

                                    cursor = mysql.connection.cursor()

                                    # Collecting grade point of that specific grade from database
                                    resultValue = cursor.execute(
                                        "SELECT grade_point FROM grade_point_policy WHERE grade = %s and grading_policy_id = (SELECT grading_policy_id FROM university WHERE university_name = (SELECT university_name from STUDENT where username=%s));",
                                        (
                                            grade_marks,
                                            user,
                                        ),
                                    )

                                    grade_point_policy = cursor.fetchall()

                                    for grade_points in grade_point_policy:
                                        grade_point = str(grade_points[0])

                                    cursor.close()

                                    # If adding course, it will only add that course in database
                                    if action == "add-course":
                                        # Storing in database
                                        cursor = mysql.connection.cursor()
                                        cursor.execute(
                                            "INSERT INTO grade_prediction VALUES (%s, %s, %s, %s, %s)",
                                            (
                                                user,
                                                course_init,
                                                grade_marks,
                                                grade_point,
                                                credit,
                                            ),
                                        )
                                        mysql.connection.commit()
                                        cursor.close()

                                        sumGradePoint_course_info = (
                                            calculate_gradepoint("course_info")
                                        )
                                        sumCredit_course_info = get_credit(
                                            "course_info"
                                        )

                                        sumGradePoint_grade_prediction = (
                                            calculate_gradepoint("grade_prediction")
                                        )
                                        sumCredit_grade_prediction = get_credit(
                                            "grade_prediction"
                                        )

                                        try:
                                            prev_cgpa = (
                                                sumGradePoint_course_info
                                                / sumCredit_course_info
                                            )
                                        except Exception:
                                            prev_cgpa = 0

                                        try:
                                            new_cgpa = (
                                                sumGradePoint_course_info
                                                + sumGradePoint_grade_prediction
                                            ) / (
                                                sumCredit_course_info
                                                + sumCredit_grade_prediction
                                            )
                                        except Exception:
                                            new_cgpa = 0

                                        return jsonify(
                                            {
                                                "grade_marks": grade_marks,
                                                "grade_point": grade_point,
                                                "new_cgpa": round(new_cgpa, 2),
                                                "prev_cgpa": round(prev_cgpa, 2),
                                                "creditPassed": (
                                                    sumCredit_course_info
                                                    + sumCredit_grade_prediction
                                                ),
                                            }
                                        )

                                    # If editing course, it will update that course in database
                                    elif action == "edit-course":

                                        prev_course_init = request.form[
                                            "prev_course_init"
                                        ]
                                        prev_grade = request.form["prev_grade"]
                                        prev_grade_point = request.form[
                                            "prev_grade_point"
                                        ]
                                        prev_credit = request.form["prev_credit"]

                                        # Storing in database
                                        cursor = mysql.connection.cursor()
                                        cursor.execute(
                                            "UPDATE grade_prediction SET course_init=%s, grade=%s, grade_point=%s, credit=%s WHERE username=%s and course_init=%s and grade=%s and grade_point=%s and credit=%s",
                                            (
                                                course_init,
                                                grade_marks,
                                                grade_point,
                                                credit,
                                                user,
                                                prev_course_init,
                                                prev_grade,
                                                prev_grade_point,
                                                prev_credit,
                                            ),
                                        )
                                        mysql.connection.commit()
                                        cursor.close()

                                        sumGradePoint_course_info = (
                                            calculate_gradepoint("course_info")
                                        )
                                        sumCredit_course_info = get_credit(
                                            "course_info"
                                        )

                                        sumGradePoint_grade_prediction = (
                                            calculate_gradepoint("grade_prediction")
                                        )
                                        sumCredit_grade_prediction = get_credit(
                                            "grade_prediction"
                                        )

                                        try:
                                            prev_cgpa = (
                                                sumGradePoint_course_info
                                                / sumCredit_course_info
                                            )
                                        except Exception:
                                            prev_cgpa = 0

                                        try:
                                            new_cgpa = (
                                                sumGradePoint_course_info
                                                + sumGradePoint_grade_prediction
                                            ) / (
                                                sumCredit_course_info
                                                + sumCredit_grade_prediction
                                            )
                                        except Exception:
                                            new_cgpa = 0

                                        return jsonify(
                                            {
                                                "grade_marks": grade_marks,
                                                "grade_point": grade_point,
                                                "new_cgpa": round(new_cgpa, 2),
                                                "prev_cgpa": round(prev_cgpa, 2),
                                                "creditPassed": (
                                                    sumCredit_course_info
                                                    + sumCredit_grade_prediction
                                                ),
                                            }
                                        )

                                i += 2

                            else:

                                i += 2

                # If someone passes grade as input, it will have more prio than total_marks
                elif grade:
                    grade_marks = str(grade)

                    cursor = mysql.connection.cursor()

                    resultValue = cursor.execute(
                        "SELECT grade_point FROM grade_point_policy WHERE grade = %s and grading_policy_id = (SELECT grading_policy_id FROM university WHERE university_name = (SELECT university_name from STUDENT where username=%s));",
                        (
                            grade_marks,
                            user,
                        ),
                    )

                    grade_point_policy = cursor.fetchall()

                    for grade_points in grade_point_policy:
                        grade_point = str(grade_points[0])

                    cursor.close()

                    if action == "add-course":
                        # Storing in database
                        cursor = mysql.connection.cursor()
                        cursor.execute(
                            "INSERT INTO grade_prediction VALUES (%s, %s, %s, %s, %s)",
                            (user, course_init, grade_marks, grade_point, credit),
                        )
                        mysql.connection.commit()
                        cursor.close()

                        sumGradePoint_course_info = calculate_gradepoint("course_info")
                        sumCredit_course_info = get_credit("course_info")

                        sumGradePoint_grade_prediction = calculate_gradepoint(
                            "grade_prediction"
                        )
                        sumCredit_grade_prediction = get_credit("grade_prediction")

                        try:
                            prev_cgpa = (
                                sumGradePoint_course_info
                                / sumCredit_course_info
                            )
                        except Exception:
                            prev_cgpa = 0

                        try:
                            new_cgpa = (
                                sumGradePoint_course_info
                                + sumGradePoint_grade_prediction
                            ) / (
                                sumCredit_course_info
                                + sumCredit_grade_prediction
                            )
                        except Exception:
                            new_cgpa = 0

                        return jsonify(
                            {
                                "grade_marks": grade_marks,
                                "grade_point": grade_point,
                                "new_cgpa": round(new_cgpa, 2),
                                "prev_cgpa": round(prev_cgpa, 2),
                                "creditPassed": (
                                    sumCredit_course_info + sumCredit_grade_prediction
                                ),
                            }
                        )

                    elif action == "edit-course":

                        prev_course_init = request.form["prev_course_init"]
                        prev_grade = request.form["prev_grade"]
                        prev_grade_point = request.form["prev_grade_point"]
                        prev_credit = request.form["prev_credit"]

                        # Storing in database
                        cursor = mysql.connection.cursor()
                        cursor.execute(
                            "UPDATE grade_prediction SET course_init=%s, grade=%s, grade_point=%s, credit=%s WHERE username=%s and course_init=%s and grade=%s and grade_point=%s and credit=%s",
                            (
                                course_init,
                                grade_marks,
                                grade_point,
                                credit,
                                user,
                                prev_course_init,
                                prev_grade,
                                prev_grade_point,
                                prev_credit,
                            ),
                        )
                        mysql.connection.commit()
                        cursor.close()

                        sumGradePoint_course_info = calculate_gradepoint("course_info")
                        sumCredit_course_info = get_credit("course_info")

                        sumGradePoint_grade_prediction = calculate_gradepoint(
                            "grade_prediction"
                        )
                        sumCredit_grade_prediction = get_credit("grade_prediction")

                        try:
                            prev_cgpa = (
                                sumGradePoint_course_info
                                / sumCredit_course_info
                            )
                        except Exception:
                            prev_cgpa = 0

                        try:
                            new_cgpa = (
                                sumGradePoint_course_info
                                + sumGradePoint_grade_prediction
                            ) / (
                                sumCredit_course_info
                                + sumCredit_grade_prediction
                            )
                        except Exception:
                            new_cgpa = 0

                        return jsonify(
                            {
                                "grade_marks": grade_marks,
                                "grade_point": grade_point,
                                "new_cgpa": round(new_cgpa, 2),
                                "prev_cgpa": round(prev_cgpa, 2),
                                "creditPassed": (
                                    sumCredit_course_info + sumCredit_grade_prediction
                                ),
                            }
                        )

            # DELETE ACTION
            elif action == "delete":
                course_init = request.form["course_init"]
                grade = request.form["grade"]
                grade_point = request.form["grade_point"]
                credit = request.form["credit"]

                cursor = mysql.connection.cursor()
                cursor.execute(
                    "DELETE FROM grade_prediction WHERE username = %s and course_init = %s and grade = %s and grade_point = %s and credit = %s",
                    (user, course_init, grade, grade_point, credit),
                )
                mysql.connection.commit()
                cursor.close()

                sumGradePoint_course_info = calculate_gradepoint("course_info")
                sumCredit_course_info = get_credit("course_info")

                sumGradePoint_grade_prediction = calculate_gradepoint(
                    "grade_prediction"
                )
                sumCredit_grade_prediction = get_credit("grade_prediction")

                try:
                    prev_cgpa = (
                        sumGradePoint_course_info
                        / sumCredit_course_info
                    )
                except Exception:
                    prev_cgpa = 0

                try:
                    new_cgpa = (
                        sumGradePoint_course_info
                        + sumGradePoint_grade_prediction
                    ) / (
                        sumCredit_course_info
                        + sumCredit_grade_prediction
                    )
                except Exception:
                    new_cgpa = 0


                return jsonify(
                    {
                        "Status": "OK",
                        "new_cgpa": round(new_cgpa, 2),
                        "prev_cgpa": round(prev_cgpa, 2),
                        "creditPassed": (
                            sumCredit_course_info + sumCredit_grade_prediction
                        ),
                    }
                )

            return jsonify({"error": "Something went wrong!"})

        else:
            cursor = mysql.connection.cursor()
            resultValue = cursor.execute("SELECT * FROM grade_prediction")
            courseDetails = cursor.fetchall()
            cursor.close()

            sumGradePoint_course_info = calculate_gradepoint("course_info")
            sumCredit_course_info = get_credit("course_info")

            sumGradePoint_grade_prediction = calculate_gradepoint("grade_prediction")
            sumCredit_grade_prediction = get_credit("grade_prediction")

            try:
                prev_cgpa = (
                    sumGradePoint_course_info
                    / sumCredit_course_info
                )
            except Exception:
                prev_cgpa = 0

            try:
                new_cgpa = (
                    sumGradePoint_course_info
                    + sumGradePoint_grade_prediction
                ) / (
                    sumCredit_course_info
                    + sumCredit_grade_prediction
                )
            except Exception:
                new_cgpa = 0

            total_credit_passed = sumCredit_course_info + sumCredit_grade_prediction

            return render_template(
                "gradePrediction.html",
                courseDetails=courseDetails,
                prev_cgpa=round(prev_cgpa, 2),
                new_cgpa=round(new_cgpa, 2),
                creditPassed=total_credit_passed,
            )
    else:
        return redirect(url_for("login"))
    # return render_template("gradePrediction.html")


@app.route("/retake")
def retake_output():

    if "user" in session:

        user = session["user"]

        if request.method == "POST":

            action = request.form["action"]

            # If the post action is adding course or editing course
            if action == "add-course" or action == "edit-course":

                # Gathering info from ajax post request data
                course_init = request.form["course_init"]
                grade = request.form["grade"]
                total_marks = request.form["total_marks"]
                credit = request.form["credit"]

                # If user only pass the total mark
                if total_marks and not grade:
                    cursor = mysql.connection.cursor()
                    resultValue = cursor.execute(
                        "SELECT * FROM grading_policy WHERE grading_policy_id = 1"
                    )
                    grading_policy = cursor.fetchall()
                    for grade_num in grading_policy:
                        i = 1
                        while i <= 23:
                            if grade_num[i]:
                                if grade_num[i] >= round(
                                    float(total_marks)
                                ) and grade_num[i + 1] <= round(float(total_marks)):
                                    # grade_marks = grade_num[i]
                                    store_index = i
                                    cursor.close()
                                    if store_index == 1:
                                        grade_marks = "A+"
                                    elif store_index == 3:
                                        grade_marks = "A"
                                    elif store_index == 5:
                                        grade_marks = "A-"
                                    elif store_index == 7:
                                        grade_marks = "B+"
                                    elif store_index == 9:
                                        grade_marks = "B"
                                    elif store_index == 11:
                                        grade_marks = "B-"
                                    elif store_index == 13:
                                        grade_marks = "C+"
                                    elif store_index == 15:
                                        grade_marks = "C"
                                    elif store_index == 17:
                                        grade_marks = "C-"
                                    elif store_index == 19:
                                        grade_marks = "D+"
                                    elif store_index == 21:
                                        grade_marks = "D"
                                    elif store_index == 23:
                                        grade_marks = "F"

                                    cursor = mysql.connection.cursor()

                                    # Collecting grade point of that specific grade from database
                                    resultValue = cursor.execute(
                                        "SELECT grade_point FROM grade_point_policy WHERE grade = %s and grading_policy_id = (SELECT grading_policy_id FROM university WHERE university_name = (SELECT university_name from STUDENT where username=%s));",
                                        (
                                            grade_marks,
                                            user,
                                        ),
                                    )

                                    grade_point_policy = cursor.fetchall()

                                    for grade_points in grade_point_policy:
                                        grade_point = str(grade_points[0])

                                    cursor.close()

                                    # If adding course, it will only add that course in database
                                    if action == "add-course":
                                        # Storing in database
                                        cursor = mysql.connection.cursor()
                                        cursor.execute(
                                            "INSERT INTO course_info VALUES (%s, %s, %s, %s, %s)",
                                            (
                                                user,
                                                course_init,
                                                grade_marks,
                                                grade_point,
                                                credit,
                                            ),
                                        )
                                        mysql.connection.commit()
                                        cursor.close()

                                        sumGradePoint = calculate_gradepoint(
                                            "course_info"
                                        )
                                        sumCredit = get_credit("course_info")

                                        # cgpa = sumGradePoint / sumCredit
                                        try:
                                            cgpa = sumGradePoint / sumCredit
                                        except Exception:
                                            cgpa = 0

                                        return jsonify(
                                            {
                                                "grade_marks": grade_marks,
                                                "grade_point": grade_point,
                                                "cgpa": round(cgpa, 2),
                                                "creditPassed": sumCredit,
                                            }
                                        )

                                    # If editing course, it will update that course in database
                                    elif action == "edit-course":

                                        prev_course_init = request.form[
                                            "prev_course_init"
                                        ]
                                        prev_grade = request.form["prev_grade"]
                                        prev_grade_point = request.form[
                                            "prev_grade_point"
                                        ]
                                        prev_credit = request.form["prev_credit"]

                                        # Storing in database
                                        cursor = mysql.connection.cursor()
                                        cursor.execute(
                                            "UPDATE course_info SET course_init=%s, grade=%s, grade_point=%s, credit=%s WHERE username=%s and course_init=%s and grade=%s and grade_point=%s and credit=%s",
                                            (
                                                course_init,
                                                grade_marks,
                                                grade_point,
                                                credit,
                                                user,
                                                prev_course_init,
                                                prev_grade,
                                                prev_grade_point,
                                                prev_credit,
                                            ),
                                        )
                                        mysql.connection.commit()
                                        cursor.close()

                                        sumGradePoint = calculate_gradepoint(
                                            "course_info"
                                        )
                                        sumCredit = get_credit("course_info")

                                        # cgpa = sumGradePoint / sumCredit
                                        try:
                                            cgpa = sumGradePoint / sumCredit
                                        except Exception:
                                            cgpa = 0

                                        return jsonify(
                                            {
                                                "grade_marks": grade_marks,
                                                "grade_point": grade_point,
                                                "cgpa": round(cgpa, 2),
                                                "creditPassed": sumCredit,
                                            }
                                        )

                                i += 2

                            else:

                                i += 2

                # If someone passes grade as input, it will have more prio than total_marks
                elif grade:
                    grade_marks = str(grade)

                    cursor = mysql.connection.cursor()

                    resultValue = cursor.execute(
                        "SELECT grade_point FROM grade_point_policy WHERE grade = %s and grading_policy_id = (SELECT grading_policy_id FROM university WHERE university_name = (SELECT university_name from STUDENT where username=%s));",
                        (
                            grade_marks,
                            user,
                        ),
                    )

                    grade_point_policy = cursor.fetchall()

                    for grade_points in grade_point_policy:
                        grade_point = str(grade_points[0])

                    cursor.close()

                    if action == "add-course":
                        # Storing in database
                        cursor = mysql.connection.cursor()
                        cursor.execute(
                            "INSERT INTO course_info VALUES (%s, %s, %s, %s, %s)",
                            (user, course_init, grade_marks, grade_point, credit),
                        )
                        mysql.connection.commit()
                        cursor.close()

                        sumGradePoint = calculate_gradepoint("course_info")
                        sumCredit = get_credit("course_info")

                        # cgpa = sumGradePoint / sumCredit
                        try:
                            cgpa = sumGradePoint / sumCredit
                        except Exception:
                            cgpa = 0

                        return jsonify(
                            {
                                "grade_marks": grade_marks,
                                "grade_point": grade_point,
                                "cgpa": round(cgpa, 2),
                                "creditPassed": sumCredit,
                            }
                        )

                    elif action == "edit-course":

                        prev_course_init = request.form["prev_course_init"]
                        prev_grade = request.form["prev_grade"]
                        prev_grade_point = request.form["prev_grade_point"]
                        prev_credit = request.form["prev_credit"]

                        # Storing in database
                        cursor = mysql.connection.cursor()
                        cursor.execute(
                            "UPDATE course_info SET course_init=%s, grade=%s, grade_point=%s, credit=%s WHERE username=%s and course_init=%s and grade=%s and grade_point=%s and credit=%s",
                            (
                                course_init,
                                grade_marks,
                                grade_point,
                                credit,
                                user,
                                prev_course_init,
                                prev_grade,
                                prev_grade_point,
                                prev_credit,
                            ),
                        )
                        mysql.connection.commit()
                        cursor.close()

                        sumGradePoint = calculate_gradepoint("course_info")
                        sumCredit = get_credit("course_info")

                        # cgpa = sumGradePoint / sumCredit
                        try:
                            cgpa = sumGradePoint / sumCredit
                        except Exception:
                            cgpa = 0

                        return jsonify(
                            {
                                "grade_marks": grade_marks,
                                "grade_point": grade_point,
                                "cgpa": round(cgpa, 2),
                                "creditPassed": sumCredit,
                            }
                        )

            # DELETE ACTION
            elif action == "delete":
                course_init = request.form["course_init"]
                grade = request.form["grade"]
                grade_point = request.form["grade_point"]
                credit = request.form["credit"]

                cursor = mysql.connection.cursor()
                cursor.execute(
                    "DELETE FROM course_info WHERE username = %s and course_init = %s and grade = %s and grade_point = %s and credit = %s",
                    (user, course_init, grade, grade_point, credit),
                )
                mysql.connection.commit()
                cursor.close()

                sumGradePoint = calculate_gradepoint("course_info")
                sumCredit = get_credit("course_info")

                # cgpa = sumGradePoint / sumCredit

                try:
                    cgpa = sumGradePoint / sumCredit
                except Exception:
                    cgpa = 0

                return jsonify(
                    {"Status": "OK", "cgpa": round(cgpa, 2), "creditPassed": sumCredit}
                )

            elif action == "move-retake-course":

                course_init = request.form["course_init"]
                grade = request.form["grade"]
                grade_point = request.form["grade_point"]
                credit = request.form["credit"]

                cursor = mysql.connection.cursor()
                cursor.execute(
                    "INSERT INTO `retake_output` SELECT * FROM course_info WHERE username=%s and course_init = %s and grade = %s and grade_point = %s and credit = %s",
                    (user, course_init, grade, grade_point, credit),
                )
                cursor.execute(
                    "DELETE FROM course_info WHERE username=%s and course_init = %s and grade = %s and grade_point = %s and credit = %s",
                    (user, course_init, grade, grade_point, credit),
                )
                mysql.connection.commit()
                cursor.close()

                sumGradePoint = calculate_gradepoint("course_info")
                sumCredit = get_credit("course_info")

                # cgpa = sumGradePoint /
                try:
                    cgpa = sumGradePoint / sumCredit
                except Exception:
                    cgpa = 0

                return jsonify(
                    {"Status": "OK", "cgpa": round(cgpa, 2), "creditPassed": sumCredit}
                )


            return jsonify({"error": "Something went wrong!"})

        else:
            cursor = mysql.connection.cursor()
            resultValue = cursor.execute("SELECT * FROM retake_output")
            courseDetails = cursor.fetchall()
            cursor.close()

            sumGradePoint = calculate_gradepoint("retake_output")
            sumCredit = get_credit("retake_output")

            # cgpa = sumGradePoint /
            try:
                cgpa = sumGradePoint / sumCredit
            except Exception:
                cgpa = 0

            return render_template(
                "retakeOutput.html",
                courseDetails=courseDetails,
                cgpa=round(cgpa, 2),
                creditPassed=sumCredit,
            )
    else:
        return redirect(url_for("login"))

    # return render_template("retakeOutput.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
