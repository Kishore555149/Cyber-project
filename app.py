import os
import re
from functools import wraps

import mysql.connector
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)

# Change this key before using the application outside your own computer.
app.secret_key = os.environ.get("SECRET_KEY", "replace-this-key-before-deployment")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

# XAMPP's default MySQL settings. Update these if you changed them in XAMPP.
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "security_quiz",
}


def get_db_connection():
    """Open a connection to the local XAMPP MySQL database."""
    return mysql.connector.connect(**DB_CONFIG)


def login_required(view_function):
    """Send visitors without a login session to the login page."""
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)

    return wrapped_view


def positive_id(value):
    """Return a positive integer ID, or 404 for an invalid value."""
    try:
        parsed_value = int(value)
    except (TypeError, ValueError):
        abort(404)
    if parsed_value < 1:
        abort(404)
    return parsed_value


def question_form_values():
    """Read and validate the fields shared by add and edit question forms."""
    values = {
        field: request.form.get(field, "").strip()
        for field in ("question", "option_a", "option_b", "option_c", "option_d")
    }
    values["correct_answer"] = request.form.get("correct_answer", "").strip().upper()
    if any(not value for value in values.values()):
        return values, "Please complete every question field."
    if len(values["question"]) > 10000:
        return values, "Question text must be 10,000 characters or fewer."
    if any(len(values[field]) > 255 for field in ("option_a", "option_b", "option_c", "option_d")):
        return values, "Each answer option must be 255 characters or fewer."
    if values["correct_answer"] not in {"A", "B", "C", "D"}:
        return values, "Correct answer must be A, B, C, or D."
    return values, None


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username:
            flash("Username cannot be empty.", "error")
        elif len(username) > 50:
            flash("Username must be 50 characters or fewer.", "error")
        elif not email:
            flash("Email cannot be empty.", "error")
        elif len(email) > 100 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Enter a valid email address.", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
        else:
            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "SELECT id FROM users WHERE username = %s OR email = %s",
                    (username, email),
                )
                if cursor.fetchone():
                    flash("That username or email is already registered.", "error")
                else:
                    password_hash = generate_password_hash(password)
                    cursor.execute(
                        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (username, email, password_hash),
                    )
                    connection.commit()
                    flash("Account created. You can now log in.", "success")
                    return redirect(url_for("login"))
            finally:
                cursor.close()
                connection.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identity = request.form.get("identity", "").strip()
        password = request.form.get("password", "")
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT id, username, password FROM users "
                "WHERE username = %s OR email = %s LIMIT 1",
                (identity, identity.lower()),
            )
            user = cursor.fetchone()
        finally:
            cursor.close()
            connection.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        flash("The username/email or password was not correct.", "error")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM questions")
        total_questions = cursor.fetchone()["total"]
        cursor.execute(
            "SELECT COUNT(*) AS total FROM results WHERE user_id = %s",
            (session["user_id"],),
        )
        quiz_count = cursor.fetchone()["total"]
        cursor.execute(
            "SELECT score, total_questions, completed_at FROM results "
            "WHERE user_id = %s ORDER BY completed_at DESC, id DESC LIMIT 1",
            (session["user_id"],),
        )
        latest_result = cursor.fetchone()
    finally:
        cursor.close()
        connection.close()

    return render_template(
        "dashboard.html",
        total_questions=total_questions,
        quiz_count=quiz_count,
        latest_result=latest_result,
    )


@app.route("/quiz", methods=["GET", "POST"])
@login_required
def quiz():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, question, option_a, option_b, option_c, option_d "
            "FROM questions ORDER BY id"
        )
        questions = cursor.fetchall()

        if request.method == "POST":
            if not questions:
                flash("There are no questions yet. Add questions before starting a quiz.", "error")
                return redirect(url_for("dashboard"))

            question_ids = [question["id"] for question in questions]
            placeholders = ", ".join(["%s"] * len(question_ids))
            cursor.execute(
                f"SELECT id, correct_answer FROM questions WHERE id IN ({placeholders})",
                tuple(question_ids),
            )
            correct_answers = {row["id"]: row["correct_answer"] for row in cursor.fetchall()}
            score = sum(
                request.form.get(f"answer_{question_id}", "").upper()
                == correct_answers.get(question_id)
                for question_id in question_ids
            )
            cursor.execute(
                "INSERT INTO results (user_id, score, total_questions) VALUES (%s, %s, %s)",
                (session["user_id"], score, len(question_ids)),
            )
            connection.commit()
            result_id = cursor.lastrowid
            return redirect(url_for("result", result_id=result_id))
    finally:
        cursor.close()
        connection.close()

    return render_template("quiz.html", questions=questions)


@app.route("/result/<int:result_id>")
@login_required
def result(result_id):
    result_id = positive_id(result_id)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT score, total_questions, completed_at FROM results "
            "WHERE id = %s AND user_id = %s",
            (result_id, session["user_id"]),
        )
        quiz_result = cursor.fetchone()
    finally:
        cursor.close()
        connection.close()
    if not quiz_result:
        abort(404)
    percentage = round(quiz_result["score"] / quiz_result["total_questions"] * 100) if quiz_result["total_questions"] else 0
    return render_template("result.html", quiz_result=quiz_result, percentage=percentage)


@app.route("/results")
@login_required
def results():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, score, total_questions, completed_at FROM results "
            "WHERE user_id = %s ORDER BY completed_at DESC, id DESC",
            (session["user_id"],),
        )
        quiz_results = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
    return render_template("result.html", quiz_results=quiz_results)


@app.route("/questions")
@login_required
def questions():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM questions ORDER BY id")
        question_list = cursor.fetchall()
    finally:
        cursor.close()
        connection.close()
    return render_template("questions.html", questions=question_list)


@app.route("/questions/add", methods=["GET", "POST"])
@login_required
def add_question():
    if request.method == "POST":
        values, error = question_form_values()
        if error:
            flash(error, "error")
        else:
            connection = get_db_connection()
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "INSERT INTO questions "
                    "(question, option_a, option_b, option_c, option_d, correct_answer) "
                    "VALUES (%s, %s, %s, %s, %s, %s)",
                    tuple(values[field] for field in (
                        "question", "option_a", "option_b", "option_c", "option_d", "correct_answer"
                    )),
                )
                connection.commit()
                flash("Question added.", "success")
                return redirect(url_for("questions"))
            finally:
                cursor.close()
                connection.close()
        return render_template("add_question.html", values=values)
    return render_template("add_question.html", values={})


@app.route("/questions/<int:question_id>/edit", methods=["GET", "POST"])
@login_required
def edit_question(question_id):
    question_id = positive_id(question_id)
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
        question = cursor.fetchone()
        if not question:
            abort(404)

        if request.method == "POST":
            values, error = question_form_values()
            if error:
                flash(error, "error")
                question.update(values)
            else:
                cursor.execute(
                    "UPDATE questions SET question = %s, option_a = %s, option_b = %s, "
                    "option_c = %s, option_d = %s, correct_answer = %s WHERE id = %s",
                    tuple(values[field] for field in (
                        "question", "option_a", "option_b", "option_c", "option_d", "correct_answer"
                    )) + (question_id,),
                )
                connection.commit()
                flash("Question updated.", "success")
                return redirect(url_for("questions"))
    finally:
        cursor.close()
        connection.close()
    return render_template("edit_question.html", question=question)


@app.route("/questions/<int:question_id>/delete", methods=["POST"])
@login_required
def delete_question(question_id):
    question_id = positive_id(question_id)
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))
        connection.commit()
        if cursor.rowcount == 0:
            abort(404)
    finally:
        cursor.close()
        connection.close()
    flash("Question deleted.", "success")
    return redirect(url_for("questions"))


@app.errorhandler(mysql.connector.Error)
def database_error(error):
    app.logger.exception("MySQL operation failed", exc_info=error)
    return (
        "The application could not access its database. Start MySQL in XAMPP and check "
        "the database settings and imported schema.",
        503,
    )


@app.errorhandler(500)
def internal_error(_error):
    return "Something went wrong. Please try again.", 500


if __name__ == "__main__":
    # Debug is off so technical tracebacks are not shown in the browser.
    app.run(host="127.0.0.1", port=5000, debug=False)