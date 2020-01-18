from flask import Flask, render_template, request
from flask_scss import Scss
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
app = Flask(__name__)
Scss(app)


@app.route('/search', methods=['POST'])
def search():
    cred = credentials.Certificate('serviceaccount.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    make = request.form.get('make')
    model = request.form.get('model')
    year = request.form.get('year')
    cars = db.collection(u'users').stream()
    car_ids = []
    for car in cars:
        car_ids.append(car.id)
    for car_id in card_ids:
        cars_user = db.collection(u'users')
    return "test"


@app.route('/')
def home():
    # Use the application default credentials
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
