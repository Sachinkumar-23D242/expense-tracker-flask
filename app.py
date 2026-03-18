from flask import Flask, render_template, request, redirect
import mysql.connector
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import os
  
app = Flask(__name__)

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sachin@012",
    database="expense_tracker"
)

cursor = conn.cursor()

# Home page (form)
@app.route('/')
def index():
    return render_template('index.html')

# Add transaction
@app.route('/add', methods=['POST'])
def add():
    amount = request.form['amount']
    category = request.form['category']
    date = request.form['date']

    query = "INSERT INTO transactions (amount, category, txn_date) VALUES (%s, %s, %s)"
    cursor.execute(query, (amount, category, date))
    conn.commit()

    return redirect('/')   # ✅ go back to home page

# View transactions
@app.route('/view')
def view():
    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()
    return render_template('view.html', data=data)
@app.route('/delete/<int:id>')
def delete(id):
    query = "DELETE FROM transactions WHERE txn_id = %s"
    cursor.execute(query, (id,))
    conn.commit()
    return redirect('/view')
@app.route('/edit/<int:id>')
def edit(id):
    cursor.execute("SELECT * FROM transactions WHERE txn_id = %s", (id,))
    data = cursor.fetchone()
    return render_template('edit.html', data=data)
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    amount = request.form['amount']
    category = request.form['category']
    date = request.form['date']

    query = "UPDATE transactions SET amount=%s, category=%s, txn_date=%s WHERE txn_id=%s"
    cursor.execute(query, (amount, category, date, id))
    conn.commit()

    return redirect('/view')

@app.route('/analytics')
def analytics():
    # Total spending
    cursor.execute("SELECT SUM(amount) FROM transactions")
    total = cursor.fetchone()[0]

    # Category-wise data
    cursor.execute("SELECT category, SUM(amount) FROM transactions GROUP BY category")
    category_data = cursor.fetchall()

    categories = [row[0] for row in category_data]
    amounts = [row[1] for row in category_data]

    # Create chart
    plt.clf()
    plt.bar(categories, amounts)
    plt.title("Category-wise Spending")

    # Add values on top (optional but nice)
    for i, v in enumerate(amounts):
        plt.text(i, v, str(v), ha='center')

    # Save chart
    os.makedirs("static", exist_ok=True)
    chart_path = "static/chart.png"
    plt.savefig(chart_path)

    return render_template(
        'analytics.html',
        total=total,
        category_data=category_data,
        chart=chart_path
    )

# Run app
if __name__ == '__main__':
    app.run(debug=True)