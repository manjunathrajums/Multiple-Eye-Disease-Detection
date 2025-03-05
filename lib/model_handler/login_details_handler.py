from lib.models.login_model import Login
from passlib.hash import sha256_crypt as sha256
from lib.extensions import mongo
from flask import jsonify
import uuid
class Login_handler:
    def __init__(self,email,password):
        self.email = email
        self.password = password

    def signup(self):
        self.password = sha256.hash(self.password)
        user_details = Login().signup()   
        user_details['email'] = self.email
        user_details['password'] = self.password
        user_uuid = str(uuid.uuid4())
        user_details['uuid'] = user_uuid
        mongo.db.logindata.insert_one(user_details)
        return True
    
    def login(self):
        user_details = mongo.db.logindata.find_one({"email":self.email})
        if not user_details:
            return {"user":False,"password":False}
        if not sha256.verify(self.password, user_details["password"]):
            return {"user":True,"password":False}
        return {"user":True,"password":True}

    

    
