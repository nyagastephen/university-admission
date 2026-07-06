import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
  
class Config:
      
    UPLOAD_FOLDER = os.path.join(
        BASE_DIR,
        "uploads"
        )

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024 
      
    SECRET_KEY="your_secret_key_here"

    SQLALCHEMY_DATABASE_URI="mysql+pymysql://root:kaycol@localhost/admission_portal"

    SQLALCHEMY_TRACK_MODIFICATIONS=False


