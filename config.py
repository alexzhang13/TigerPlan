from logging import disable
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dummy-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
    'postgresql+psycopg2://postgres:alex@localhost/tigerplan').replace(
    'postgres://', 'postgresql://') 
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    JSONIFY_PRETTYPRINT_REGULAR = True
    CAS_SERVER = "ldap.cs.princeton.edu"
    CAS_AFTER_LOGIN = 'route_root'