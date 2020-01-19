from flask import Flask, render_template, request, redirect
from google.cloud.storage.blob import Blob
from flask_scss import Scss
import firebase_admin
import datetime
from google.auth import compute_engine
from google.auth.transport import requests

from firebase_admin import credentials, storage
from firebase_admin import firestore, auth
app = Flask(__name__)
Scss(app)



logged_user = None
cred = credentials.Certificate('carbazaar-32cea-ec7ddc537cbe.json')
fbapp = firebase_admin.initialize_app(cred, {
    'storageBucket': 'carbazaar-32cea.appspot.com',
})
auth_request = requests.Request()
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


def get_cars_from_user(email):
    db = firestore.client()
    garage = db.collection(u'users').document(email).collection('garage').stream()
    cars = []
    bucket = storage.bucket(app=fbapp)
    signing_credentials = compute_engine.IDTokenCredentials(auth_request, "",
                                                            service_account_email=cred.service_account_email)

    for car in garage:
        print(car.to_dict()['user_images'])
        images = []
        for image in car.to_dict()['user_images']:
            try:
                print(cred, image)
                images.append(Blob.from_string(image).generate_signed_url(datetime.timedelta(seconds=300), credentials=signing_credentials))
            except Exception as e:
                print(e)
                print("Improper URL")
        print(images)
        path = car.to_dict()['Model'].path
        mk, ml = get_mk_ml(str(path))
        mk = str(mk)
        ml = str(ml)

        cars.append({
                'user': email,
                "make": mk,
                "model": ml,
                "images": images,
                "history": car.to_dict()['History']
        })
    return cars

@app.route('/search', methods=['POST'])
def search():
    db = firestore.client()
    make_g = request.form.get('make')
    model_g = request.form.get('model')
    year_g = request.form.get('year')
    users = db.collection(u'users').stream()
    user_ids = []
    cars = []
    bucket = storage.bucket(app=fbapp)
    for user in users:
        user_ids.append(user.id)
    for user_id in user_ids:
        garage = db.collection(u'users').document(user_id).collection('garage').stream()
        for car in garage:
            images = [bucket.blob(image).generate_signed_url(datetime.timedelta(seconds=300), method='GET') for image in car.to_dict()['user_images']]
            path = car.to_dict()['Model'].path
            mk, ml = get_mk_ml(str(path))
            mk = str(mk)
            ml = str(ml)
            if mk == str(make_g) and ml == str(model_g):
                cars.append({
                    'user': user_id,
                    "make": mk,
                    "model": ml,
                    "images": images,
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

    return render_template("home.html", logged_in=logged_in(), cars=get_cars_from_user(logged_user.email))


if __name__ == '__main__':
    app.run()
