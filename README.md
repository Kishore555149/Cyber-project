# Cybersecurity Security Awareness Quiz System

A beginner-friendly Level-3 college mini project. Learners create an account, sign in, take a cybersecurity awareness quiz and review their scores. Signed-in users can also create, read, update and delete quiz questions.

## Features

- Registration and login with Werkzeug password hashing
- Session-based authentication for dashboard, quiz, results and question pages
- Security quiz with automatically calculated and saved results
- Dashboard statistics: question count, latest score and quizzes completed
- Question CRUD (create, read, update and delete)
- Input checks, parameterized SQL statements and Jinja2's default HTML escaping
- Responsive HTML and CSS; no React, Node.js, Docker or cloud database

Every signed-in account can manage the shared question bank in this teaching version. A production system should add roles so only trusted administrators can change questions.

## Technologies

Python 3, Flask, MySQL on XAMPP, `mysql-connector-python`, HTML5, CSS3, Jinja2 and Werkzeug password hashing.

## Folder structure

```text
security_quiz/
|-- app.py
|-- database.sql
|-- requirements.txt
|-- README.md
|-- templates/
|   |-- base.html
|   |-- login.html
|   |-- register.html
|   |-- dashboard.html
|   |-- quiz.html
|   |-- result.html
|   |-- questions.html
|   |-- add_question.html
|   `-- edit_question.html
`-- static/
    `-- style.css
```

## Setup on Windows

### 1. Start XAMPP

Install XAMPP if it is not already installed. Open the XAMPP Control Panel and click **Start** beside **Apache** and **MySQL**. The Flask app connects to MySQL on `localhost` as `root` with a blank password by default. If your XAMPP MySQL password differs, update `DB_CONFIG` near the top of `app.py`.

### 2. Create the database

1. Open `http://localhost/phpmyadmin` in a browser.
2. Select **Import**.
3. Choose this project's `database.sql` file.
4. Click **Import** or **Go**. The script creates `security_quiz`, its three tables and ten starter questions.

You can confirm the import by selecting `security_quiz` in phpMyAdmin and checking for `users`, `questions` and `results`.

### 3. Create and activate a Python virtual environment

Open PowerShell in the project folder. These commands use the workspace location in this environment; change the path if you put the project elsewhere.

```powershell
Set-Location "$HOME\Documents\New folder"
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once for the current terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 4. Install packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the application

Keep XAMPP MySQL running, then run the required command from the project folder:

```powershell
python app.py
```

Open **http://127.0.0.1:5000** in Chrome. Stop the development server with `Ctrl+C` in PowerShell.

## Exact Windows command sequence

The workspace folder is the project folder and already contains the files. To create/open that folder explicitly, then install and run the app:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\Documents\New folder"
code "$HOME\Documents\New folder"
Set-Location "$HOME\Documents\New folder"
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If XAMPP is installed in its default location, open its control panel with:

```powershell
Start-Process "C:\xampp\xampp-control.exe"
```

Click **Start** beside Apache and MySQL, then open phpMyAdmin:

```powershell
Start-Process "http://localhost/phpmyadmin"
```

In phpMyAdmin, select **Import**, choose `database.sql` from the project folder and click **Go**. This import step is performed in phpMyAdmin's browser interface.

Then, in the activated project terminal, run:

```powershell
python app.py
```

In another PowerShell window, open the site in Chrome:

```powershell
Start-Process "chrome.exe" "http://127.0.0.1:5000"
```

Browse to `http://127.0.0.1:5000`. The SQL import is done in phpMyAdmin rather than a shell command so the steps also work for students new to MySQL.

## First-use test procedure

1. **Registration:** Select **Create account**. Enter a username, email and a password of at least six characters. Try the same username/email again to see the duplicate warning.
2. **Login:** Sign in with either the registered username or email and password. Try a wrong password to confirm it is rejected.
3. **Dashboard:** Confirm the welcome message, question count, quiz count and latest-score area appear. Before your first quiz, the latest score is shown as `--`.
4. **Quiz:** Select **Start a quiz**, choose answers for the questions, and submit. Unanswered questions count as incorrect.
5. **Score:** Confirm the score and percentage on the completion page. The result is saved for the logged-in user.
6. **View results:** Return to the dashboard and open **View results**. The completed quiz should be listed, with a link to its score.
7. **Add question:** Open **Questions** then **Add question**. Complete all fields, choose a correct answer and save. The question appears in the list and future quizzes.
8. **Edit question:** Select **Edit**, change a field and save. Confirm the updated value in the question table.
9. **Delete question:** Select **Delete** and confirm the browser prompt. Confirm that row is removed.
10. **Logout:** Select **Log out**. Visiting a protected page such as `/dashboard` should send you to the login page.

## How question CRUD works

The question management page reads the `questions` table. The add form inserts a new row, the edit form updates a row by its ID, and the delete form removes a row by its ID. All database values are passed as connector parameters rather than joined into SQL text. Question management requires login, but this demo does not have separate administrator roles.

## Security features

- Passwords are stored as one-way Werkzeug hashes, never as plain text.
- Flask sessions remember the signed-in user's ID and username. The session cookie is HTTP-only and uses `SameSite=Lax`.
- A login-required decorator protects dashboard, quiz, score and question routes.
- User input is checked for required fields, password length, email shape and valid answer letters.
- SQL queries use `%s` parameters. IDs are checked before database operations, and score lookup is limited to the current user.
- Jinja2 autoescapes values in HTML templates. The database password is only in the Python configuration, not rendered into a page.
- The built-in server runs with debug disabled and database failures return a safe message instead of SQL details.

This is an educational local project, not a production deployment. For real use, set a long random `SECRET_KEY`, use a dedicated MySQL account with limited permissions, add CSRF protection and administrator roles, and serve Flask behind a production web server over HTTPS.

## Screenshots for college submission

Capture the registration page, login page, dashboard, quiz with options, completed result, results history, question list, add-question form, edit-question form and the database tables in phpMyAdmin. Use test data only; do not include a real password or private personal information in screenshots.

## Project explanation in simple English

This application teaches users how to recognize common cybersecurity risks. Flask receives the browser's form submissions and runs the application logic. MySQL stores account records, quiz questions and results. Passwords are hashed before storage. After login, the app uses a session to know which learner is using it. The quiz checks submitted choices against the correct answers, calculates a score and saves that score for the learner.

## Project workflow

1. A learner registers; Flask validates the form and saves a password hash in `users`.
2. The learner logs in; Flask verifies the hash and starts a session.
3. The dashboard reads question and result counts from MySQL.
4. The learner submits quiz choices; Flask checks answers and stores a row in `results`.
5. The learner can review saved scores or maintain the shared question bank.
6. Logging out clears the session.

## Database explanation

- `users` stores each unique username, email, password hash and registration time.
- `questions` stores the prompt, four choices and the correct answer letter.
- `results` stores a learner's score, the number of questions and completion time. Its `user_id` foreign key links the score to `users`.

`database.sql` creates the database and tables, then inserts ten example awareness questions the first time the question table is empty.

## Viva questions and simple answers

1. **What is Flask?** A small Python web framework used to create web routes and handle requests.
2. **What is MySQL used for here?** It stores users, quiz questions and quiz results.
3. **Why hash passwords?** A hash prevents the original password from being stored directly in the database.
4. **What is a session?** Data that lets the app recognize a logged-in user across requests.
5. **What is CRUD?** Create, Read, Update and Delete; these actions manage quiz questions.
6. **How does the app reduce SQL injection risk?** It sends input as query parameters instead of combining it into SQL text.
7. **What does the `results.user_id` foreign key do?** It links a result to a real user record.
8. **How is the quiz score calculated?** The selected letter for each question is compared with its stored correct letter and correct choices are counted.
9. **Why validate form input?** To reject missing or invalid values before saving them.
10. **What is Jinja2?** Flask's template engine, which fills HTML pages with data and escapes displayed values by default.

## Future enhancements

- Add administrator and learner roles with permission checks.
- Add CSRF protection and password reset/change flows.
- Add topic categories, difficulty levels, random question selection and a timer.
- Add charts, score trends and exportable reports.
- Add more validation, automated tests, database migrations and a production deployment configuration.