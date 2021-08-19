from flask import Flask
import pymongo
# A function to create the Flask application which will connect our front end HTML files to our backend Python scripts
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secretkey'
    from .views import views
    app.register_blueprint(views,url_prefix='/')
    
    return app