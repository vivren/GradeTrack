import dash
from flask import Flask
import dash_bootstrap_components as dbc

external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Balsamiq+Sans&family=Epilogue:ital,wght@1,500&family=Lobster+Two&family=Poppins:wght@300&family=Sora:wght@500&display=swap',
     dbc.themes.BOOTSTRAP
]

server = Flask(__name__)

app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)
app.css.config.serve_locally = True
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://master:password@gradetrack.cmoor2gacvn8.us-east-1.rds.amazonaws.com/gradetrack"

