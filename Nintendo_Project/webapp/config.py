import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	WTF_CSRF_ENABLED = True
	SQLALCHEMY_DATABASE_URI = "postgresql://josephberkowitz:@localhost:5432/nintendo"
	SQLALCHEMY_TRACK_MODIFICATIONS = False
