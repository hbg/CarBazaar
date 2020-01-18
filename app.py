from flask import Flask, render_template, request
from flask_scss import Scss
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, auth
app = Flask(__name__)
Scss(app)
cred = credentials.Certificate('serviceaccount.json')
firebase_admin.initialize_app(cred)
logged_user = None

def get_mk_ml(s):
    return s.split('cars/')[1].split('/models/')[0], s.split('cars/')[1].split('/models/')[1]


@app.route('/login', methods=['GET','POST'])
def login():
    global logged_user
    if request.method == 'POST':

        try:
            user = auth.get_user_by_email(request.form['email'])
            assert request.form['password'] == user.password
            logged_user = user
            return render_template()
        except:
            "Incorrect password"
            return render_template("login.html", message="Invalid email or password.")
    return render_template("login.html")

@app.route('/search', methods=['POST'])
def search():
    db = firestore.client()
    make_g = request.form.get('make')
    model_g = request.form.get('model')
    year_g = request.form.get('year')
    users = db.collection(u'users').stream()
    user_ids = []
    cars = []
    for user in users:
        user_ids.append(user.id)
    for user_id in user_ids:
        garage = db.collection(u'users').document(user_id).collection('garage').stream()
        for car in garage:
            path = car.to_dict()['Model'].path
            mk, ml = get_mk_ml(str(path))
            mk = str(mk)
            ml = str(ml)
            if mk == str(make_g) and ml == str(model_g):
                cars.append({
                    'user': user_id,
                    "make": mk,
                    "model": ml,
                    "history": car.to_dict()['History']
                })
            car_entry = db.document(path).get()
            print(car_entry.to_dict())
    return str(cars)


@app.route('/')
def home():
    # Use the application default credentials
    return render_template("index.html")


if __name__ == '__main__':
    app.run()
