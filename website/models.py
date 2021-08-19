from flask import Flask, jsonify, request, session, redirect
import uuid
from passlib.hash import pbkdf2_sha256
import pymongo

## This python file was created to handle all things related to working with the login database
## Handles creating a new user
## Checking to see if a user has lready registered with the same information
## Handles logging into an existing user
## Checking to see if a user has logged in with the correct credentials
## Creating a session of the current user which can be used through the program 
## Creating the schema to add to the external database
## Encypting the password and other private information


## Connecting to the database
client = pymongo.MongoClient("mongodb+srv://admin:123a@cluster0.9n27l.mongodb.net/Users?retryWrites=true&w=majority")
db = client.test
globalUser = ""

class User:
    # This function starts a session when the user logs in
    # The session will also be cleared once a user logs out
    # Without a session being created the functionality of the application is about 0%
    def start_session(self,user):
        global globalUser
        del user['password']
        session['logged_in'] = True
        session['user'] = user
        #print(user)
        globalUser = user['email'] 
        return jsonify(user),200

    # Creates a blank schema with fields for ID #, Name, Email, Password (encrypted), 2 arrays for the movies we will either watch or not watch, and IDs for those movies
    # The password is encrypted so users information is protected
    # Checks to see if an email is already in the database, if it is we will throw an error and not signup the new user
    # Insert the user with the given fields from the registration HTML into the database
    def signup(self):
        user = {
            "_id": uuid.uuid4().hex,
            "name": request.form.get('name'),
            "email": request.form.get('email'),
            "password": request.form.get('password'),
            "watch": [],
            "dontWatch":[],
            "id":[],
        }

        user['password'] = pbkdf2_sha256.encrypt(user['password'])
        if db.Users.find_one({"email": user['email']}):
            return jsonify({"error":"Email address already in use"}),400
        if db.Users.insert_one(user):
            self.start_session(user)
        return jsonify(user), 200
    # Clears the session so the user will be logged out
    # Redirects the user to the login page
    def signout(self):
        global globalUser 
        globalUser = ""
        session.clear()
        return redirect('/login')
    # Grabs the login information from the login HTML webpage
    # Checks the database to see if the inputted email is registered within the database
    # Throws an error if the email is not present
    # If the email is present it will check both encrpyted passwords so see if they are EXACTLY the same
    # Logs in and calls the create session function 
    def login(self):
        global globalUser
        #print("dasdas")
        #print(request.form.get('username'))
        user = db.Users.find_one({
            "email": request.form.get('username')
        })
        
        if user and pbkdf2_sha256.verify(request.form.get('password'),user['password']): 
            globalUser = user
            return self.start_session(user)

        return jsonify({"error":"invadli"}),401

    # Helper function so other python files can know what user is logged in by checking the session
    def getSession(self):
        #print(globalUser)
        return globalUser