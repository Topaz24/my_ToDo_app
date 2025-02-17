import os
from flask import Flask, render_template, url_for, redirect, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Get database credentials from environment variables
DB_user_name = os.getenv('MYSQL_USER', 'todo_user')  # Default value if not set in env
DB_pass = os.getenv('MYSQL_PASSWORD', '1234')  # Default value if not set in env
DB_address = os.getenv('DB_HOST', 'db')  # Use 'db' as service name in Docker Compose
DB_name = os.getenv('MYSQL_DATABASE', 'ToDoDB')  # Default value if not set in env

# Set up Flask app
app = Flask(__name__)

# Configure the database URI with environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_user_name}:{DB_pass}@{DB_address}/{DB_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the TasksTable model
class TasksTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/', methods=["GET", "POST"])
def main():
    if request.method == "POST":
        if "task" in request.form:
            task = request.form["task"]
            due_str = request.form.get("due_date")
            if due_str:
                due_date = datetime.strptime(due_str, "%Y-%m-%dT%H:%M")
            else:
                due_date = None
            # Add a new task to the database
            new_task = TasksTable(task=task, due_date=due_date)
            db.session.add(new_task)
            db.session.commit()

        elif "delete last" in request.form:
            last_task = TasksTable.query.order_by(TasksTable.id.desc()).first()
            if last_task:
                db.session.delete(last_task)
                db.session.commit()

        elif "delete" in request.form:
            to_delete = request.form["delete"]
            task = TasksTable.query.filter_by(task=to_delete).first()
            if task:
                db.session.delete(task)
                db.session.commit()

        elif "done" in request.form:
            toggle = request.form["done"]
            task = TasksTable.query.filter_by(task=toggle).first()
            if task:
                task.done = not task.done
                db.session.commit()

    tasks = TasksTable.query.all()
    return render_template("base.html", tasks=tasks, current_date=datetime.now())

if __name__ == '__main__':
    app.run(debug=True)

