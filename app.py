import pymysql
import os
import base64
import io
import json

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

dbUrl = 'mysql+pymysql://root:''@localhost/second-test'
#db_url = 'mysql+pymysql://root:root123@34.101.247.201/Users?unix_socket=/cloudsql/my-project-33757-api:asia-southeast2:test123-instance'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_SECRET_KEY']= "secret1"
app.config['SQLALCHEMY_DATABASE_URI'] = dbUrl
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db = SQLAlchemy(app)
jwt = JWTManager(app)


class Users(db.Model):
    username = db.Column(db.String(50))
    password = db.Column(db.String(100))
    email = db.Column(db.String(100), primary_key=True)
    picture = db.Column(db.LargeBinary)

with app.app_context():
    db.create_all()

def get_response_image(image_path):
    pil_img = Image.open(image_path, mode='r') # reads the PIL image
    byte_arr = io.BytesIO()
    pil_img.save(byte_arr, format='PNG') # convert the PIL image to byte array
    encoded_img = base64.encodebytes(byte_arr.getvalue()).decode('ascii') # encode as base64
    return encoded_img

class Register(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        email = request.json.get('email')
        email_in = Users.query.filter_by(email=email).count()
        username_in = Users.query.filter_by(username=username).count()

        if email_in == 1:
            return jsonify({
                "message":"the email already used, use another email",
                "error":True
            })
        elif username_in == 1:
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
        email = request.json.get('email')
        password = request.json.get('password')
        
        user_mail = [user.email for user in Users.query.all()]
        user_pass = [user.password for user in Users.query.all()]
        userPic = [user.picture for user in Users.query.all()]
        
        if email in user_mail:
            indx = user_mail.index(email)
            
            if password == user_pass[indx]:
                accToken = create_access_token(identity=email)
                
                return make_response(jsonify(
                    {
                        "message":"Login Success",
                        "access_token": accToken,
                        "length": len(userPic)
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
        usr_email = request.json.get('email')
        email_in = Users.query.filter_by(email=usr_email).count()
        user_mail = [user.email for user in Users.query.all()]
        user_pass = [user.password for user in Users.query.all()]

        if email_in == 1:
            index = user_mail.index(usr_email)
            message = Mail(
            from_email='c151dsx0968@bangkit.academy',
            to_emails=usr_email,
            subject='Your account password',
            html_content= user_pass[index])
            try:
                sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
                response = sg.send(message)
                return make_response(jsonify({"message":"Your password is sent successfully"}),200)
            except Exception as e:
                print(e.message)
                return jsonify({"message":"fail to send password"})
        return jsonify({"message":"you haven't registered yet"})

class Upload(Resource):
    @jwt_required()
    def post(self):
        currentUser = get_jwt_identity()
        return jsonify({"email":currentUser})

class History(Resource):
    @jwt_required()
    def get(self):
        pass


class Profile(Resource):    
    @jwt_required()
    def get(self):
        currentUser = get_jwt_identity()
        gettingPic = Users.query.filter_by(email=currentUser).first()
        readPic = gettingPic.picture
        byteFile = io.BytesIO(readPic)
        encoded_img = get_response_image(byteFile)

        
        
        return make_response(jsonify({
            "username":gettingPic.username,
            "img": encoded_img,
        }),200)
    
    @jwt_required()
    def put(self):
        currentUser = get_jwt_identity()
        file = request.files['file']
        userBase = [user.email for user in Users.query.all()]
        userPic = [user.email for user in Users.query.all()]
        emailIndex = userBase.index(currentUser)
        num_rows_updated = Users.query.filter_by(email=currentUser).update(dict(picture=file.read()))
        db.session.commit()
        encoded_img = get_response_image(file)
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
    app.run(debug=True)