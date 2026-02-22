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
        title = request.form.get("title").strip()
        type = request.form.get("type")
        dateStr = request.form.get("date")
        location = request.form.get("location").strip()
        description = request.form.get("description").strip()

        if not title or not type or not dateStr or not location or not description:
            return render_template("new.html", error="Tous les champs sont obligatoires.")

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
    
    if request.method == "POST":
        db.session.delete(event)
        db.session.commit()

    return redirect(url_for("list_event"))


@app.route("/api/events/upcoming/<proposed_date>", methods= ["GET"])
def next_events(proposed_date):
    try:
        proposed_date = datetime.strptime(proposed_date, "%Y-%m-%d").date()

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Format de la date invalide."
        }), 400

    events = Events.query.filter(Events.date >= proposed_date).order_by(Events.date.asc()).limit(5).all()

    eventsList = []
    for event in events:
        eventsList.append({
            "id": event.id,
            "title": event.title,
            "type": event.type,
            "date": event.date.isoformat(),
            "location": event.location,
            "description": event.description
        })

    return jsonify({
        "status": "success",
        "count": len(eventsList),
        "data": eventsList
    }), 200


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)