from flask import Blueprint, render_template, request, jsonify, make_response
import json
from PIL import Image
import  urllib
from random import randint
from urllib.request import urlopen
from website.models import User
import pymongo
client = pymongo.MongoClient("mongodb+srv://admin:123a@cluster0.9n27l.mongodb.net/Users?retryWrites=true&w=majority")
db = client.test.Users
page = 1
pageTV = 1
baseDetailUrl = "https://api.themoviedb.org/3/movie/movie_id?api_key=31657fcbc4dc6a9f0e0277b60a6314e9&language=en-US"

baseUrl = "https://api.themoviedb.org/3/discover/movie?api_key=31657fcbc4dc6a9f0e0277b60a6314e9&language=en-US&pg=2&sort_by=popularity.desc&with_genres="
baseUrlTV = "https://api.themoviedb.org/3/discover/tv?api_key=31657fcbc4dc6a9f0e0277b60a6314e9&language=en-US&pg=2&sort_by=popularity.desc&with_genres="
genreSet = False
viewingTV = False

tempUrl = ""
tempUrl = baseUrl + str(page)
tempUrlTV = ""
tempUrlTV = baseUrlTV + str(pageTV)

runningUrl = ""
runningUrlTV = ""

json_obj = urlopen(baseUrl)
json_objTV = urlopen(baseUrlTV)

data = json.load(json_obj)
dataTV = json.load(json_objTV)

var = data['results']
varTV = dataTV['results']

list_len = len(data['results'])
list_lenTV = len(dataTV['results'])

dontWatch = []
watch = []

dontWatchTitle = []
watchTitle = []

idArray= []


excludeGenres = []
testWatch = ['sunny','rainy','cloud']
i = 0
iTV = 0
constantString = ""
constantStringTV = ""

views = Blueprint('views', __name__)


# Flask Function that will route the origin website link + /signup to a certain HTML or function within the program
# In this case 127.0.0.1:5000/signup
@views.route('/signup', methods=['POST'])
def signup():
    return User().signup()

# Flask Function that will route the origin website link + /signin to a certain HTML or function within the program
# In this case 127.0.0.1:5000/signin
@views.route('/signin', methods=['POST'])
def signin():
    return User().login()    
# Flask function that will route the default/origin website link to the index html which will serve as the "homepage"
# 127.0.0.1:5000 will always reroute to index unless we are signed out of a session in which case we will be rerouted to the signing HTML
@views.route('/', methods=['GET','POST'])
def home():
    return render_template("index.html")
# Flask Function that will route the origin website link + /genre to a certain HTML or function within the program
# In this case 127.0.0.1:5000/genre
@views.route('/genre', methods=['GET','POST'])
def genreTest():
    return render_template("genreTest.html")
# Flask Function that will route the origin website link + /login to a certain HTML or function within the program
# In this case 127.0.0.1:5000/login
@views.route('/login', methods=['GET','POST'])
def loginTest():
    return render_template("login.html")
# Flask Function that will route the origin website link + /register to a certain HTML or function within the program
# In this case 127.0.0.1:5000/register
@views.route('/register')
def registerTest():
    return render_template("signup.html")
# Flask Function that will route the origin website link + /listTest to a certain HTML or function within the program
# In this case 127.0.0.1:5000/listTest
@views.route('/listTest')
def listTest():
    return render_template("listTest.html")    
# Flask Function that will route the origin website link + /listNoTest to a certain HTML or function within the program
# In this case 127.0.0.1:5000/listNoTest
@views.route('/listNoTest')
def listNoTest():
    return render_template("listNoTest.html")   

# Flask Function that will route the origin website link + /listInfo to a certain HTML or function within the program
# In this case 127.0.0.1:5000/listInfo
@views.route('/listInfo')
def listInfo():
    return render_template("listMovieDetails.html")        

# Flask Function that will route the origin website link + /listInfo to a certain HTML or function within the program
# In this case 127.0.0.1:5000/signin
@views.route('/signout')
def signout():
    return User().signout()  

# This is a function that is created using Flask
# It allows us to directly get data from the HTML webpages
# It also allows us to send data from this python file to the HTML webpages
# In this function we are specifically getting a request to send the watched list to be displayed on screen
@views.route('/setList',methods=['GET','POST'])
def setList():
    global constantString,baseUrl,i,json_obj,data,page,var,runningUrl,page
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV   
    req = request.get_json()
    getMovies()
    res = make_response(jsonify({"message": "JSON recieved", "title":watch,"id":idArray},200))
    return res

# This is a function that is created using Flask
# It allows us to directly get data from the HTML webpages
# It also allows us to send data from this python file to the HTML webpages
# In this function we are specifically getting a request to send the dontWatch list to be displayed on screen
@views.route('/setNoList',methods=['GET','POST'])
def setNoList():
    global constantString, baseUrl, i, json_obj, data, page, var, runningUrl, page
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV    
    req = request.get_json()
    getMovies()
    res = make_response(jsonify({"message": "JSON recieved", "title":dontWatch, "id":idArray},200))
    return res

# This is a function that is created using Flask
# It allows us to directly get data from the HTML webpages
# It also allows us to send data from this python file to the HTML webpages
# In this function specifcally we are being sent a request to remove an item from the database
# We take in an ID/Title of a movie or show and then promptly remove it from the database
@views.route('/removeItem',methods=['GET','POST'])
def removeItem():
    global constantString, baseUrl, i, json_obj, data, page, var, runningUrl, page  
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV  
    req = request.get_json()
    db.update(
        {"email":str(User().getSession())},
        {"$pull":{
            "watch": str(req['remove']),
            "id": str(req['removeID'])
         }}
        )
    getMovies()
    res = make_response(jsonify({"message": "JSON recieved", "title":watch},200))
    return res
# This is a function that is created using Flask
# It allows us to directly get data from the HTML webpages
# It also allows us to send data from this python file to the HTML webpages
# In this function specifcally we are being sent a request to remove an item from the database
# We take in an ID/Title of a movie or show and then promptly remove it from the database
@views.route('/removeNoItem',methods=['GET','POST'])
def removeNoItem():
    global constantString, baseUrl, i, json_obj, data, page, var, runningUrl, page
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV    
    req = request.get_json()
    db.update(
        {"email":str(User().getSession())},
        {"$pull":{
            "dontWatch": str(req['remove'])
         }}
        )
    getMovies()
    res = make_response(jsonify({"message": "JSON recieved", "title":dontWatch},200))
    return res

# This is a function that is created using Flask
# It allows us to directly get data from the HTML webpages
# It also allows us to send data from this python file to the HTML webpages
# This function is called once the user is done selecting all the genres they would like to include in their search and exclude from their search
@views.route('/setGenres', methods=['GET','POST'])
def setGenres():
    global constantString, baseUrl, i, json_obj, data, page, var, runningUrl, page
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV
    req = request.get_json()

    genreStringTV = "10759,35"
    tempUrl = ""
    tempUrlTV = ""
    runningUrl = baseUrl + req['genreString'] + "&page="
    runningUrlTV = baseUrlTV + genreStringTV + "&page="
    tempUrl = baseUrl + req['genreString'] + "&page=" + str(page)
    tempUrlTV = baseUrlTV + genreStringTV + "&page=" + str(page)

    i = 0
    json_obj = urlopen(tempUrl)
    data = json.load(json_obj)
    var = data['results']
    list_len = len(data['results'])

    if str(var[i]['title']) in str(dontWatch) or str(var[i]['title']) in str(watch):
        while str(var[i]['title']) in str(dontWatch) or str(var[i]['title']) in str(watch):
            updateMovies()
    res = make_response(jsonify({"message": "JSON recieved", "title":var[i]['title'],"rating":var[i]['vote_average'],"description":var[i]['overview'],"poster":var[i]['poster_path']},200))
    return res
# This is a function that is created using Flask
# It allows us to directly get data from the HTML webpages
# It also allows us to send data from this python file to the HTML webpages
# This function is called once the user is done selecting all the genres they would like to include in their search and exclude from their search
@views.route('/setExcludeGenres', methods=['GET','POST'])
def setExcludeGenres():
    global constantString, baseUrl, i, json_obj, data, page, var, runningUrl, page, excludeGenres
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV
    req = request.get_json()
    stringTemp = ""
    stringTemp = str(req['genreString'])
    excludeGenres = stringTemp.split(',')
    res = make_response(jsonify({"message": "JSON recieved", "title":var[i]['title'],"rating":var[i]['vote_average'],"description":var[i]['overview'],"poster":var[i]['poster_path']},200))
    return res
# This is a function that is created using Flask
# It allows us to directly get data from the HTML webpages
# It also allows us to send data from this python file to the HTML webpages
# This function is called whenever we click the do not watch button. We add the name of the movie and its ID to the MongoDB, our local do not watch list.
@views.route('/dontWatch', methods=['GET','POST'])
def dont_Watch():
    req = request.get_json()
    global constantString, baseUrl, i, json_obj, data, page, var, watch, dontWatch, idArray
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV

    if viewingTV == True:
        dontWatch.append(varTV[iTV]['name'])
        db.update(
            {"email":str(User().getSession())},
            {"$push":{
                "dontWatch": str(varTV[iTV]['name']),
            }}
            )
        updateMoviesTV()
        vid = getVideoTV()
        res = make_response(jsonify({"message": "JSON recieved", "title":varTV[iTV]['name'],"rating":varTV[iTV]['vote_average'],"description":varTV[iTV]['overview'],"poster":varTV[iTV]['poster_path'],"vid":vid},200))
    else:
        dontWatch.append(var[i]['title'])
        db.update(
            {"email":str(User().getSession())},
            {"$push":{
                "dontWatch": str(var[i]['title']),
            }}
            )
        updateMovies()
        vid = getVideo()
        res = make_response(jsonify({"message": "JSON recieved", "title":var[i]['title'],"rating":var[i]['vote_average'],"description":var[i]['overview'],"poster":var[i]['poster_path'],"vid":vid},200))
    #print(dontWatch)
    #if i == 20:
    #    tempUrl = ""
    #    i = 0
    #    page +=1
    #    tempUrl = runningUrl + str(page)
    #    json_obj = urlopen(tempUrl)
    #    data = json.load(json_obj)
    #    var = data['results']
    
    return res
# This is a function that is created using Flask
# It allows us to directly get data from the HTML webpages
# It also allows us to send data from this python file to the HTML webpages
# This function is called whenever we click the watch button. We add the name of the movie and its ID to the MongoDB and our local watch list.
@views.route('/Watch', methods=['GET','POST'])
def will_Watch():
    req = request.get_json()
    global constantString, baseUrl, i, json_obj, data, page, var, watch, dontWatch, idArray
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV
    print(viewingTV)
    if viewingTV == True:
        idArray.append(varTV[iTV]['id'])
        watch.append(varTV[iTV]['name'])
        db.update(
            {"email":str(User().getSession())},
            {"$push":{
                "watch": str(varTV[iTV]['name']),
                "id": str(varTV[iTV]['id'])
            }}
            )
        updateMoviesTV()
        print(varTV[iTV]['name'])
        vid = getVideoTV()
        res = make_response(jsonify({"message": "JSON rWecieved", "title":varTV[iTV]['name'],"rating":varTV[iTV]['vote_average'],"description":varTV[iTV]['overview'],"poster":varTV[iTV]['poster_path'],"vid":vid},200))
    else:
        idArray.append(var[i]['id'])
        watch.append(var[i]['title'])
        db.update(
            {"email":str(User().getSession())},
            {"$push":{
                "watch": str(var[i]['title']),
                "id": str(var[i]['id'])
                }}
            )
        updateMovies()
        vid = getVideo()
        res = make_response(jsonify({"message": "JSON rWecieved", "title":var[i]['title'],"rating":var[i]['vote_average'],"description":var[i]['overview'],"poster":var[i]['poster_path'],"vid":vid},200))
    
    return res
# This is a function that is created using Flask
# It allows us to directly get data from the HTML webpages
# It also allows us to send data from this python file to the HTML webpages
# This function is mainly called to check if a log in session has been created
@views.route('/checkSess', methods=['GET','POST'])
def checkSess():
    req = request.get_json()
    if User().getSession() == "":
        return jsonify({"error":User.getSession()}),400 
    return jsonify({"error":"Logged In"}),200

# This is a function that is created using Flask
# It allows us to directly get data from the HTML webpages
# It also allows us to send data from this python file to the HTML webpages
# This function is called whenever the main index.html HTML is refreshed/reloaded
# The function will make sure that the data on the screen is up to date by setting it to the current values off the database after every refresh
@views.route('/SetDefault', methods=['GET','POST'])
def SetDefault():
    req = request.get_json()
    global constantString, baseUrl, i, json_obj, data, page, var, watch, dontWatch, idArray
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV
    if User().getSession() == "":
        return jsonify({"error":"Not Logged In"}),400 
    tempdata = list(db.find({"email":str(User().getSession())}))
#
    watch = tempdata[0]['watch']
    dontWatch = tempdata[0]['dontWatch']
    skipPresent()
    vid = getVideo()
    viewingTV = False
    res = make_response(jsonify({"message": "JSON recieved", "title":var[i]['title'],"rating":var[i]['vote_average'],"description":var[i]['overview'],"poster":var[i]['poster_path'],"vid":vid},200))
    return res

@views.route('/SetDefaultTV', methods=['GET','POST'])
def SetDefaultTV():
    print("hello?")
    req = request.get_json()
    global constantString, baseUrl, i, json_obj, data, page, var, watch, dontWatch, idArray
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV
    if User().getSession() == "":
        return jsonify({"error":"Not Logged In"}),400 
    tempdata = list(db.find({"email":str(User().getSession())}))
#
    watch = tempdata[0]['watch']
    dontWatch = tempdata[0]['dontWatch']
    skipPresentTV()
    vid = getVideo()
    viewingTV = True
    res = make_response(jsonify({"message": "JSON recieved", "title":varTV[iTV]['name'],"rating":varTV[iTV]['vote_average'],"description":varTV[iTV]['overview'],"poster":varTV[iTV]['poster_path'],"vid":vid},200))
    return res
# This is a simple helper function used inconjunction with the rest of the Flask Functions
# This will moving from the current movie to the next movie after the user decides to either like or dislike the video
# This function will also handle refreshing the API key once it has visited every single entry on thr current page
def updateMovies():
    global i, constantString, baseUrl, i, json_obj, data, page, var
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV
    exclude = 878
    detailsID = baseDetailUrl
    if str(var[i]['title']) in str(dontWatch) or str(var[i]['title']) in str(watch):
        print("Movie Added To Lists and Database Succesfully")
    i += 1
    if i == 20:
        tempUrl = ""
        i = 0
        page +=1
        tempUrl = runningUrl + str(page)
        print(tempUrl)
        json_obj = urlopen(tempUrl)
        data = json.load(json_obj)
        var = data['results']

    testDetails = ""
    testDetails = detailsID.replace("movie_id",str(var[i]['id']))
    j = 0
    json_obj2 = urlopen(testDetails)
    data = json.load(json_obj2)
    varDetails = data['genres']
    if str(var[i]['title']) in str(dontWatch) or str(var[i]['title']) in str(watch):
        while str(var[i]['title']) in str(dontWatch) or str(var[i]['title']) in str(watch):
            updateMovies()


def updateMoviesTV():
    global i, constantString, baseUrl, i, json_obj, data, page, var
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV
    exclude = 878
    detailsID = baseDetailUrl
    if str(varTV[iTV]['name']) in str(dontWatch) or str(varTV[iTV]['name']) in str(watch):
        print("Movie Added To Lists and Database Succesfully")
    iTV += 1
    if iTV == 20:
        tempUrlTV = ""
        iTV = 0
        pageTV +=1
        tempUrlTV = runningUrlTV + str(pageTV)
        print(tempUrlTV)
        print(tempUrlTV)
        print("$$$$$$$$$$$$$")
        print(iTV)
        print(tempUrlTV)
        print("$$$$$$$$$$$$$")
        json_objTV = urlopen(tempUrlTV)
        dataTV = json.load(json_objTV)
        varTV = dataTV['results']

    if str(varTV[iTV]['name']) in str(dontWatch) or str(varTV[iTV]['name']) in str(watch):
        while str(varTV[iTV]['name']) in str(dontWatch) or str(varTV[iTV]['name']) in str(watch):
            updateMoviesTV()

# This is a helper function used to skip all movies/shows that we have already visited on new reloads or sign ins
def skipPresent():
    if str(var[i]['title']) in str(dontWatch) or str(var[i]['title']) in str(watch):
        while str(var[i]['title']) in str(dontWatch) or str(var[i]['title']) in str(watch):
            updateMovies()


def skipPresentTV():
    if str(varTV[iTV]['name']) in str(dontWatch) or str(varTV[iTV]['name']) in str(watch):
        while str(varTV[iTV]['name']) in str(dontWatch) or str(varTV[iTV]['name']) in str(watch):
            updateMoviesTV()


# A function created to grab the user's watch and do not watch lists from the database so they do not have to explore the same movies
def getMovies():
    global dontWatch, watch, idArray
    global constantStringTV,baseUrlTV,iTV,json_objTV,dataTV,pageTV,varTV,runningUrlTV,pageTV,viewingTV
    tempdata = list(db.find({"email":str(User().getSession())}))
    watch = tempdata[0]['watch']
    dontWatch = tempdata[0]['dontWatch']
    idArray = tempdata[0]['id']
# A function created to make a new API key to specifcally explore the current movie so we can grab its youtube URL link.
def getVideo():
    vidUrl = "http://api.themoviedb.org/3/movie/movie_id/videos?api_key=31657fcbc4dc6a9f0e0277b60a6314e9"
    tempVid = vidUrl.replace("movie_id", str(var[i]['id']))
    json_obj3 = urlopen(tempVid)
    data = json.load(json_obj3)
    varVid = data['results']
    youtubeUrl = "https://www.youtube.com/embed/"
    try:   
        finUrl = youtubeUrl + varVid[0]['key']
    except:
        finUrl = "https://www.youtube.com/embed/dQw4w9WgXcQ"
    return finUrl

def getVideoTV():
    vidUrlTV = "http://api.themoviedb.org/3/tv/tv_id/videos?api_key=31657fcbc4dc6a9f0e0277b60a6314e9"
    tempVidTV = vidUrlTV.replace("tv_id", str(varTV[iTV]['id']))
    print(tempVidTV)
    json_obj3 = urlopen(tempVidTV)
    data = json.load(json_obj3)
    varVid = data['results']
    youtubeUrl = "https://www.youtube.com/embed/" 
    print('#####################################')
    print(varTV[iTV]['id'])
    print(varVid)
    print('#####################################')
    try:
        finUrl = youtubeUrl + varVid[0]['key']
    except:
        finUrl = "https://www.youtube.com/embed/dQw4w9WgXcQ"
    return finUrl