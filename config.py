import os

class Config:
    SECRET_KEY = "taller_nacho_secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///taller.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
