import dash
from flask import Flask
import dash_bootstrap_components as dbc

server = Flask(__name__)

app = dash.Dash(__name__, server=server, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.server.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://master:password@gradetrack.cmoor2gacvn8.us-east-1.rds.amazonaws.com/gradetrack"

