from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from  datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)




class Events(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50), nullable = False)
    type = db.Column(db.String(50), nullable = False)
    date = db.Column(db.Date, nullable = False)
    location = db.Column(db.String(128), nullable = False)
    description = db.Column(db.Text, nullable = False)
    date_add = db.Column(db.DateTime, default = db.func.current_timestamp())

    def __repr__(self):
        return f"Events('{self.title}', '{self.type}', '{self.date}', '{self.location}')"


@app.route("/", methods = ["GET"])
def list_event():
    events = Events.query.all()
    return render_template("index.html", events=events)


@app.route("/new", methods = ["GET", "POST"])
def new_event():
    if request.method == "POST":
        #action = request.form.get("action", "")
        title = request.form.get("title")
        type = request.form.get("type")
        dateStr = request.form.get("date")
        location = request.form.get("location")
        description = request.form.get("description")

        dateformated = datetime.strptime(dateStr, '%Y-%m-%d').date()

        event= Events(title=title, type=type, date=dateformated, location=location, description=description)
        db.session.add(event)
        db.session.commit()

        return redirect(url_for("list_event"))

    return render_template("new.html")

    

@app.route("/delete/<int:event_id>", methods = ["GET", "POST"])
def delete_event(event_id):
    event = Events.query.get(event_id)
    if not event:
        return redirect(url_for("list_event"))
    
    db.session.delete(event)
    db.session.commit()

    return redirect(url_for("list_event"))

@app.route("/api", methods= ["GET", "POST"])
def next_events(proposedDate):
    if (not proposedDate isinstance datetime)

    events = Events.query.filter(Events.date > proposedDate).order_by(Events.date.asc()).limit(5).all()


    return jsonify(events, status=200, mimetype = "application/json")
    #return render_template("api.html", events = events)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)