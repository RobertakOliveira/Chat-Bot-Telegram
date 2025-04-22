from flask import Flask
from controllers.main_controller import Main

app = Flask(__name__)

app.add_url_rule('/', "main", Main)