from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_PATH = 'hostel_mess_demo.db'

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']

        if role == 'admin':
            # Hardcoded admin login (you can use DB for this too)
            if username == 'admin' and password == 'admin123':
                session['user'] = 'admin'
                return redirect('/admin')
            else:
                return "Invalid admin credentials", 401

        elif role == 'student':
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT roll, name, password FROM students WHERE roll = ?", (username,))
            student = c.fetchone()
            conn.close()
            if student and password == student[2]:  # student[2] is password
                session['user'] = student[0]  # roll
                return redirect('/student')
            else:
                return "Invalid student credentials", 401

    return render_template('login.html')

@app.route('/student')
def student():
    if 'user' in session and session['user'] != 'admin':
        roll = session['user']
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Get monthly mess records
        c.execute("SELECT month, days_present, fee FROM mess_records WHERE roll = ?", (roll,))
        records = c.fetchall()

        # Calculate total due
        c.execute("SELECT dues FROM students WHERE roll = ?", (roll,))
        total_due = c.fetchone()[0]

        conn.close()

        return render_template('student.html', records=records, total_due=total_due)
    return redirect('/login')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' in session and session['user'] == 'admin':
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        if request.method == 'POST':
            roll = request.form['roll']
            month = request.form['month']
            days = int(request.form['days'])
            fee = days * 100

            # Update student dues
            c.execute("UPDATE students SET dues = dues + ? WHERE roll = ?", (fee, roll))

            # Insert into mess_records
            c.execute("INSERT INTO mess_records (roll, month, days_present, fee) VALUES (?, ?, ?, ?)",
                      (roll, month, days, fee))

            conn.commit()

        c.execute("SELECT roll, name, dues FROM students")
        students = c.fetchall()
        conn.close()

        return render_template('admin.html', students=students)
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
