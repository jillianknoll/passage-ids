__author__ = 'ADI Labs'
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
import requests

app = Flask(__name__)
app.config["DEBUG"] = True




@app.route("/")
def home():
	return "Hello World"


if __name__ == '__main__':
	app.run()