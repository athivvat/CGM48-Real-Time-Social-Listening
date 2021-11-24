from dotenv import dotenv_values
from flask import Flask

config = dotenv_values("../.env")

app = Flask(__name__)
app.run(config['FLASK_PORT'])