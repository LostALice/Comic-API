#Code by AkinoAlice@Tyrant_Rex

from flask import Flask,jsonify
from api import nhentai

app = Flask(__name__,static_folder="/")

@app.route("/")
def index_():
    return "May be nothing here"

@app.route("/<code>")
def index(code):
    return jsonify(nhentai(code).info),jsonify(nhentai(code).image())

if __name__ == "__main__":
    app.run("0.0.0.0")
