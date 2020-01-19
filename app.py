from flask import Flask, render_template, request, redirect
from flask_scss import Scss
import firebase_admin
import datetime
from uuid import uuid4
from google.auth.transport import requests
from firebase_admin import credentials
from gcloud import storage

from firebase_admin import firestore, auth

app = Flask(__name__)

logged_user = None
cred = credentials.Certificate('carbazaar-32cea-ec7ddc537cbe.json')
fbapp = firebase_admin.initialize_app(cred, {
    'storageBucket': 'carbazaar-32cea.appspot.com',
})
client = storage.Client(credentials=cred)
storage_client = storage.Client.from_service_account_json('carbazaar-32cea-ec7ddc537cbe.json')

auth_request = requests.Request()
VINS = [

]


def logged_in():
    return logged_user is not None


def get_mk_ml(s):
    return s.split('cars/')[1].split('/models/')[0], s.split('cars/')[1].split('/models/')[1]


@app.route('/users/<username>/<uuid>')
def retrieve_mini_post(username, uuid):
    db = firestore.client()
    pst = db.collection("users").document(username).collection("garage").document(uuid).get()
    post_details = pst.to_dict()
    pth = post_details['Model'].path
    make, model = get_mk_ml(pth)

    return render_template("car_mini.html", details=post_details, make=make, model=model)


@app.route('/register', methods=['GET', 'POST'])
def register():
    global logged_user
    if request.method == "POST":
        try:
            user = auth.create_user(
                email=request.form.get("email"),
                email_verified=False,
                password=request.form.get("email"),
                disabled=False)
        except:
            return render_template("register.html", logged_in=logged_in(), message="Email is already in use.")
        logged_user = user
    return render_template("register.html", logged_in=logged_in(), page_name="Register")


@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_user
    if request.method == 'POST':

        try:
            user = auth.get_user_by_email(request.form['email'])
            # assert request.form['password'] == user.password
            logged_user = user
            return redirect('/garage')
        except Exception as e:
            print(e)
            "Incorrect password"
            return render_template("login.html", message="Invalid email or password.")
    return render_template("login.html", logged_in=logged_in(), page_name="Log In")


def get_cars_from_user(email):
    db = firestore.client()
    garage = db.collection(u'users').document(email).collection('garage').stream()
    cars = []
    bucket = storage_client.bucket('carbazaar-32cea.appspot.com')

    for car in garage:
        uuid  = car.id
        print(car.to_dict()['user_images'])
        images = []
        for image in car.to_dict()['user_images']:
            try:
                print(cred, image)
                if 'gs://' in image:
                    image = image.split('gs://carbazaar-32cea.appspot.com/')[1]
                    print(image)
                    images.append(bucket.blob(image).generate_signed_url(datetime.timedelta(seconds=300)))
                else:
                    images.append(image)
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
            "history": car.to_dict()['History'],
            "id": uuid
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
    bucket = storage_client.bucket('carbazaar-32cea.appspot.com')
    for user in users:
        user_ids.append(user.id)
    for user_id in user_ids:
        garage = db.collection(u'users').document(user_id).collection('garage').stream()
        for car in garage:
            images = []
            path = car.to_dict()['Model'].path
            mk, ml = get_mk_ml(str(path))
            print(mk, ml, make_g, model_g)
            mk = str(mk)
            ml = str(ml)
            image = car.to_dict()['user_images'][0]
            uuid = car.id
            if 'gs://' in image:
                image = image.split('gs://carbazaar-32cea.appspot.com/')[1]
                print(image)
                images.extend(bucket.blob(image).generate_signed_url(datetime.timedelta(seconds=300)))
                thumbnail = ''.join(images)
                print(thumbnail)
            else:
                thumbnail = image
                print(image)
            if mk == str(make_g) and ml == str(model_g) and car.to_dict().get('selling'):
                cars.append({
                    'user': user_id,
                    "make": mk,
                    "model": ml,
                    "image": thumbnail,
                    "history": car.to_dict()['History'],
                    "id": uuid
                })
        print(cars)
        return render_template("search_results.html", cars=cars, logged_in=logged_in(), page_name="Explore")


@app.route('/')
def home():
    return render_template("index.html", logged_in=logged_in(), page_name="Home")


@app.route('/logout')
def logout():
    global logged_user
    logged_user = None
    return redirect('/')


@app.route('/garage')
def garage():
    global logged_user
    # Use the application default credentials
    if logged_user is None:
        return redirect('/login')

    return render_template("home.html", logged_in=logged_in(), cars=get_cars_from_user(logged_user.email), page_name="My Garage")


@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    global logged_user
    db = firestore.client()
    if request.method == 'POST' and logged_in():
        make = request.form.get("make")
        model = request.form.get("model")
        year = request.form.get("year")
        owner_exp = request.form.get("owner_experience")
        price = request.form.get("price")
        image = request.form.get("image")
        selling = request.form.get("sellingTF")
        doc = db.collection("cars").document(make).collection("models").document(model).set({
            "site_images": []
        }, merge=True)
        db.collection("users").document(logged_user.email).collection("garage").document(str(uuid4())).set({
            "price": price,
            "owner_exp": owner_exp,
            "user_images": [image],
            "selling": selling,
            "Model": db.collection("cars").document(make).collection("models").document(model),
            "history": []
        })
        return redirect('/garage')
    elif not logged_user:
        return redirect('/login')
    return render_template("add_car.html", logged_in=logged_in(), cars=get_cars_from_user(logged_user.email), page_name="Add Car")


if __name__ == '__main__':
    app.run()
