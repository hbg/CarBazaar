from flask import Flask, render_template, request, redirect
from flask_scss import Scss
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore, auth
app = Flask(__name__)
Scss(app)

logged_user = None
cred = credentials.Certificate('serviceaccount.json')
firebase_admin.initialize_app(cred)
VINS = [
    {
        "VIN"

    }
]

def logged_in():
    return logged_user is not None


def get_mk_ml(s):
    return s.split('cars/')[1].split('/models/')[0], s.split('cars/')[1].split('/models/')[1]


@app.route('/login', methods=['GET','POST'])
def login():
    global logged_user
    if request.method == 'POST':

        try:
            user = auth.get_user_by_email(request.form['email'])
            #assert request.form['password'] == user.password
            logged_user = user
            return redirect('/garage')
        except Exception as e:
            print(e)
            "Incorrect password"
            return render_template("login.html", message="Invalid email or password.")
    return render_template("login.html", logged_in=logged_in())

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
    return render_template("search_results.html", cars=cars, logged_in=logged_in())


@app.route('/')
def home():
    return render_template("index.html", logged_in=logged_in())


@app.route('/garage')
def garage():
    global logged_user
    # Use the application default credentials
    if logged_user is None:
        return redirect('/login')
    return render_template("home.html", logged_in=logged_in())


if __name__ == '__main__':
    app.run()
