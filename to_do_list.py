from flask import Flask, render_template, url_for, redirect, request
from datetime import datetime
app=Flask(__name__)
arr=[]
states=[] #so i can track if a task is done or not
due_dates=[] #to track the dates
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
            arr.append(task)
            states.append(False)
            due_dates.append(due_date)
        elif "delete last" in request.form:
            arr.pop()
            states.pop()
            due_dates.pop()
        elif "delete" in request.form:
            index=arr.index(request.form["delete"])
            states.pop(index) #removing if the task is done according to index
            arr.pop(index)
            due_dates.pop(index)
        elif "done" in request.form:
            toggle=request.form["done"]
            if toggle in arr: #is there a need for it..?
                index=arr.index(toggle)
                states[index]= not states[index]
            #this way if its false itll be sent as true and if true will be sent as false, so change the colors.       
    return render_template("base.html",arr=arr,states=states,due_dates=due_dates,current_date=datetime.now())
app.run()