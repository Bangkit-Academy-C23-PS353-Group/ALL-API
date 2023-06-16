import pymysql
import os
import base64
import io
import tensorflow as tf
import numpy as np
import cv2

from keras.models import load_model
import gcsfs
import h5py
from datetime import datetime
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from PIL import Image
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import Flask, request, make_response,jsonify
from flask_cors import CORS
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)
CORS(app)

#dbUrl = 'mysql+pymysql://root:''@localhost/second-test'
#dburl = 'mysql+pymysql://<username>:<password>@localhost/<database name>'
dbUrl = 'mysql+pymysql://root:root123@34.72.3.0/ALL?unix_socket/cloudsql/cs23-ps353-group:us-central1:c23-ps353-instance'
#dburl = 'mysql+pymysql://<username>:<password>@<public ip>/<database name>?unix_socket/cloudsql/<connection name>'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_SECRET_KEY']= "secret1"
app.config['SQLALCHEMY_DATABASE_URI'] = dbUrl
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= True

PROJECT_NAME = 'CS23-PS353-Group'
CREDENTIALS = 'cs23-ps353-group-b1dec43c8b96.json' #google cloud storage credentials

db = SQLAlchemy(app)
jwt = JWTManager(app)#authorization & authentication flask jwt extended




class Users(db.Model): #database model user
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100), primary_key=True)
    picture = db.Column(db.LargeBinary)

class Historis(db.Model): #histori
    email = db.Column(db.String(100), db.ForeignKey('users.email'))
    patient = db.Column(db.String(50))
    result = db.Column(db.String(50))
    id = db.Column(db.Integer, primary_key=True)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)   

with app.app_context():
    db.create_all() #

def getImage(imagePath):
    pilImg = Image.open(imagePath, mode='r') # reads the PIL image
    byteArr = io.BytesIO()
    pilImg.save(byteArr, format='PNG') # convert the PIL image to byte array
    encodedImg = base64.encodebytes(byteArr.getvalue()).decode('ascii') # encode as base64
    return encodedImg



def loadmodel():
    MODEL_PATH = 'cs23-ps353-group.appspot.com/static/my_model.h5'
    FS = gcsfs.GCSFileSystem(project=PROJECT_NAME, token=CREDENTIALS)
    with FS.open(MODEL_PATH, 'rb') as model_file:
        model_gcs = h5py.File(model_file, 'r')
        model = load_model(model_gcs)
    return model

model = loadmodel()
categories = ['Benign', 'Early', 'Pre', 'Pro']

def input_samples(img_result):
    x = tf.keras.preprocessing.image.img_to_array(img_result)
    x = np.expand_dims(x, axis=0)
    x = x / 255
    images = np.vstack([x])
    return images

def process_image(uploaded_file):
    # Convert the bytes file using OpenCV image
    image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), cv2.IMREAD_COLOR)

    #segmentation 
    light_orange = (168, 50, 50)
    dark_orange = (182, 255, 255)
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(image_hsv, light_orange, dark_orange)
    img_result = cv2.bitwise_and(image_hsv, image_hsv, mask=mask)
    img_result = cv2.resize(img_result, (150, 150))

    output_buffer = cv2.imencode('.jpg', img_result)[1].tobytes()

    # Save segmentation image to Google Cloud Storage
    BUCKET_NAME = 'cs23-ps353-group.appspot.com'  
    FILENAME = f'{uploaded_file.filename}.jpg'  

    client = storage.Client.from_service_account_json(CREDENTIALS)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(FILENAME)
    blob.upload_from_string(output_buffer, content_type='image/jpeg')

    # Perform inference on the processed image
    input_data = input_samples(img_result)
    classes = model.predict(input_data, batch_size=20)
    predicted_class = np.argmax(classes, axis=1)
    result = categories[int(predicted_class)]

    return result

class Register(Resource):
    def post(self):
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        emailIn = Users.query.filter_by(email=email).count()
        usernameIn = Users.query.filter_by(username=username).count()

        if emailIn == 1:
            return jsonify({
                "message":"the email already used, use another email",
                "error":True
            })
        elif usernameIn == 1:
            return jsonify({
                "message":"the username already used, use another username",
                "error":True
            })
        elif email and password and username:
            data = Users(username=username,password=password,email=email)
            db.session.add(data)
            db.session.commit()
            return make_response(jsonify(
                {
                    "message":"Registration Success",
                    "data":{
                        "username": username,
                        "email": email,
                    }
                 }),200 )
        
        return make_response(jsonify(
            {
                "message":"Registration Failed", 
                "error":True
            },400))
        
class Login(Resource):
    def post(self):
        email = request.form.get('email')
        password = request.form.get('password')
        
        userMail = [user.email for user in Users.query.all()]
        userPass = [user.password for user in Users.query.all()] # get all password
        
        if email in userMail:
            indx = userMail.index(email)
            
            if password == userPass[indx]:
                accToken = create_access_token(identity=email)
                
                return make_response(jsonify(
                    {
                        "message":"Login Success",
                        "access_token": accToken,
                    }
                ),200)
            return(jsonify({
                "message":"Wrong Password",
            }))
        return jsonify({
            "message":"Login Failed"
        })


class ForgotPass(Resource):
    def post(self):
        email = request.form.get('email')
        emailIn = Users.query.filter_by(email=email).count()
        userMail = [user.email for user in Users.query.all()] # get all email  in database
        userPass = [user.password for user in Users.query.all()] #get all pass in database

        if emailIn == 1:
            index = userMail.index(email)
            message = Mail(
            from_email='c151dsx0968@bangkit.academy',
            to_emails=email,
            subject='Your account password',
            html_content= userPass[index])
            try:
                sendgrid_client = SendGridAPIClient('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')
                response = sendgrid_client.send(message)
                print("Email sent successfully!")
                return make_response(jsonify({"message":"Your password is sent successfully"}),200)
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
        return jsonify({"message":"you haven't registered yet"})

class Upload(Resource):
    @jwt_required()
    def post(self):
        currentUser = get_jwt_identity()
        uploaded_file = request.files['file']
        patient_name = request.form.get('patient')
        
        result = ''
        result = process_image(uploaded_file)
        
        data = Historis(email=currentUser,patient=patient_name,result=result)
        db.session.add(data)
        db.session.commit()
        return make_response(jsonify(
        {
            "result":result,
            "patient":patient_name
        }),200)

class History(Resource):
    @jwt_required()
    def get(self):
        currentUser = get_jwt_identity()
        getHistory = Historis.query.filter_by(email=currentUser).all()
        storeHistory = []
        for history in getHistory:
            storeHistory.append([history.patient,history.result,history.createdAt])
            
        return make_response(jsonify(storeHistory),200)


class Profile(Resource):    
    @jwt_required()
    def get(self):
        currentUser = get_jwt_identity()
        gettingPic = Users.query.filter_by(email=currentUser).first()
        readPic = gettingPic.picture #.BLOB
        byteFile = io.BytesIO(readPic)
        encodedImg = getImage(byteFile)

        
        
        return make_response(jsonify({
            "username":gettingPic.username,
            "img": encodedImg,
        }),200)
    
    @jwt_required()
    def put(self):
        currentUser = get_jwt_identity()
        file = request.files['file']
        userBase = [user.email for user in Users.query.all()]
        emailIndex = userBase.index(currentUser)
        updatePic = Users.query.filter_by(email=currentUser).update(dict(picture=file.read()))
        db.session.commit()
        encoded_img = getImage(file)
        return make_response(jsonify(
            {
                "message":"Photo has been changed successfully",
                "encode":encoded_img,
            }
        ),200)
        
    

api.add_resource(Register, "/register", methods=["POST"])
api.add_resource(Login, "/login", methods=["POST"])
api.add_resource(ForgotPass,"/forgot-pass",methods=["POST"])
api.add_resource(Upload,"/upload",methods=["POST"])
api.add_resource(History, "/history",methods=["GET"])
api.add_resource(Profile, "/profile",methods=["GET","PUT"])



if __name__=="__main__":
    app.run(port=8080, debug=True)
