from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import random
import os

load_dotenv()

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
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route("/random", methods=['GET'])
def cafe_selection_random():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all", methods=['GET'])
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    all_cafes_dict = {"Cafes": []}
    for cafe in cafes:
        all_cafes_dict["Cafes"].append(cafe.to_dict())
    return jsonify(all_cafes_dict)

@app.route("/search")
def search():
    error_msg = {
        "error": {
            "Not Found": "Sorry, we don't have a cafe at that location."
        }
    }
    query_location = request.args.get("loc")
    # print(query_location)
    search_result = Cafe.query.filter_by(location=query_location).first()
    # print(search_result)
    if search_result:
        return jsonify(search_result.to_dict())
    else:
        return jsonify(error_msg)


## HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
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


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=['GET', 'PATCH'])
def update_cafe(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        ## Just add the code after the jsonify method. 200 = Ok
        return jsonify(response={"success": "Successfully updated the price."}), 200
    else:
        #404 = Resource not found
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


## HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=['GET', 'DELETE'])
def delete_cafe(cafe_id):
    api_key = request.args.get("api_key")
    cafe_to_delete = db.session.query(Cafe).get(cafe_id)
    if api_key == os.environ['API_KEY']:
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": f"Successfully removed cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(response={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api key."}), 403



if __name__ == '__main__':
    app.run(debug=True)
