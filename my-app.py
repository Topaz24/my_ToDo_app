from flask import Flask, render_template, url_for, redirect, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

DB_user_name = 'todo_user'
DB_pass = '1234'
DB_address = 'localhost'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_user_name}:{DB_pass}@{DB_address}/ToDoDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class TasksTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, server_default=False)
    due_date= db.Column(db.DateTime, nullable=True)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/', methods=["GET","POST"])
def main():
    if request.method=="POST":
        if "task" in request.form:
            task=request.form["task"]
            due_str=request.form.get("due_date")
            if due_str:
                due_date=datetime.strptime(due_str, "%Y-%m-%dT%H:%M")
            else:
                due_date=None
            #add a new task to db
            new_task=TasksTable(task=task,due_date=due_date)
            db.session.add(new_task)
            db.session.commit()

        elif "delete last" in request.form:
             #because there is no .last() ill switch its order then ask for first
            last_task = TasksTable.query.order_by(TasksTable.id.desc()).first()
            if last_task:
                db.session.delete(last_task)
                db.session.commit()

        elif "delete" in request.form:
            to_delete=request.form["delete"]
            task = TasksTable.query.filter_by(task=to_delete)
            if task:
                db.session.delete(task)
                db.session.commit()

        elif "done" in request.form:
            toggle=request.form["done"]
            task = TasksTable.query.filter_by(task=toggle.first())
            if task: #checks if the task object is not null
                task.done = not task.done 
                db.session.commit()
             #this way if its false itll be sent as true and if true will be sent as false, so change the colors.
    
    tasks = TasksTable.query.all() #get all the table info from the                
    return render_template("base.html",tasks=tasks,current_date=datetime.now())

if __name__ == '__main__':
    app.run(debug=True)