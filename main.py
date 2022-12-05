from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random as R

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name)for column in self.__table__.columns}

@app.route("/")
def home():
    return render_template("index.html")
    
@app.route("/random")
def random():
    cafes = db.session.query(Cafe).all()
    random_cafe = R.choice(cafes)
    return jsonify(cafe= random_cafe.to_dict())

@app.route("/all")
def all():
    all_cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route("/search")
def search():
    loc = request.args.get("loc")
    cafe = Cafe.query.filter_by(location=loc).first()
    print(cafe)
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={
            "Not Found": "Sorry, we don't have a cafe at that location."
        })

@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        #change all these to request.args.get() instead since we are retrieving from the url itself.
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    cafe = Cafe.query.filter_by(id=cafe_id).first()
    if cafe:
        cafe.coffee_price = request.args.get("updated_coffee_price")
        db.session.commit()
        return jsonify(response=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def report_closed(cafe_id):
    cafe_to_delete = Cafe.query.filter_by(id=cafe_id).first()
    if cafe_to_delete:
        inputted_secret_key = request.args.get("api-key")
        if inputted_secret_key == "TopSecretAPIKey":
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response=f"Cafe of id {cafe_id} was successfully deleted from the database."), 200
        else:
            return jsonify(error={"No Access": "Sorry, that's not allowed, you do not have access for deletion."}), 403
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
