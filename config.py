import os
from flask import Flask, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from PIL import Image
import pillow_avif  

from flask import request, jsonify, session
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from PIL import Image
import uuid
import secrets
import string
import json

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ae68177cfc47043d80d622007229de84348c9c43d36350e5b36366ddf308c454')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://postgres:postregress.$15/07/1998@localhost/drivate')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-string')
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Google OAuth Configuration
# app.config['GOOGLE_OAUTH_CLIENT_ID'] = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
# app.config['GOOGLE_OAUTH_CLIENT_SECRET'] = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')

# Initialize extensions
db = SQLAlchemy(app)
# bcrypt = Bcrypt(app)
# jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173", "http://localhost:5174", "http://192.168.1.125:5173"])

# CORS configuration
CORS(app, origins=["http://localhost:5173", "http://localhost:5174", "http://192.168.1.125:5173"])

# File upload configuration
UPLOAD_FOLDER = 'uploads'
CAROUSEL_FOLDER = 'static/images/carousel'
MAKE_LOGO = 'static/images/make_logos'
BODY_LOGO = 'static/images/body_logos'
VEHICLE_IMAGES = 'static/uploads'
BLOGS_FOLDER = 'static/images/blogs'
ABOUT_US_FOLDER = 'static/images/about_us'
REVIEWS_FOLDER = 'static/images/reviews'
# UPLOAD_BLOGS_FOLDER = 'static/images/blogs/uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CAROUSEL_FOLDER'] = CAROUSEL_FOLDER
app.config['MAKE_LOGO'] = MAKE_LOGO
app.config['VEHICLE_IMAGES'] = VEHICLE_IMAGES
app.config['BLOGS_FOLDER'] = BLOGS_FOLDER
app.config['ABOUT_US_FOLDER'] = ABOUT_US_FOLDER
app.config['REVIEWS_FOLDER'] = REVIEWS_FOLDER
# app.config['UPLOAD_BLOGS_FOLDER'] = UPLOAD_BLOGS_FOLDER
# app.config['CAROUSEL_FOLDER'] = 'static/images/carousel'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(CAROUSEL_FOLDER):
    os.makedirs(CAROUSEL_FOLDER)
if not os.path.exists(MAKE_LOGO):
    os.makedirs(MAKE_LOGO)
if not os.path.exists(BODY_LOGO):
    os.makedirs(BODY_LOGO)
if not os.path.exists(VEHICLE_IMAGES):
    os.makedirs(VEHICLE_IMAGES)
if not os.path.exists(BLOGS_FOLDER):
    os.makedirs(BLOGS_FOLDER)
if not os.path.exists(ABOUT_US_FOLDER):
    os.makedirs(ABOUT_US_FOLDER)
if not os.path.exists(REVIEWS_FOLDER):
    os.makedirs(REVIEWS_FOLDER)