__author__ = 'ADI Labs'
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, flash, json, session, redirect
from flask.ext.session import Session
import requests
from schema import db, Passage, User
import random
from flask.ext.sqlalchemy import SQLAlchemy
from oauth2client.client import flow_from_clientsecrets
import httplib2
import re
from QuoteForm import QuoteForm

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    db.init_app(app)
    return app, db


app, db = create_app()
app.config["DEBUG"] = True
sess = Session()

@app.before_request
def before_request():
    if session.get('type', None) is None:
        session['type'] = 0

@app.route("/")
def home():
    print(session['type'])
    if session['type'] is 0:
        content = Passage.query.all()
        randQuote = content[random.randint(0, len(content) - 1)]
    else:
        content = Passage.query.filter_by(class_type=session['type']).all()
        randQuote = content[random.randint(0, len(content) - 1)]

    return render_template("content.html", content2 = randQuote)

@app.route("/form", methods = ['GET', 'POST'])
def form():
    form = QuoteForm()
    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('form.html', form=form)
        if form.class_type.data == 0:
            flash('Please choose a class: Lit Hum or CC.')
            return render_template('form.html', form=form)
        quote = Passage(quote=form.quote.data,
                        title=form.title.data,
                        author=form.author.data,
                        submitter=form.submitter.data,
                        class_type=form.class_type.data)
        db.session.add(quote)
        db.session.commit()
        form.quote.data = None
        form.title.data = None
        form.author.data = None
        form.class_type.data = 0
        return render_template('form.html', form = form)
    elif request.method == 'GET':
        return render_template('form.html', form = form)

@app.route("/LitHum", methods = ['POST'])
def setLH():
    if request.method == "POST":
        session['type'] = 1
        return redirect('/')

@app.route("/CC", methods = ['POST'])
def setCC():
    if request.method == "POST":
        session['type'] = 2
        return redirect('/')

@app.errorhandler(404)
def page_not_found(error):
    return "Sorry, this page was not found.", 404

CU_EMAIL_REGEX = r"^(?P<uni>[a-z\d]+)@.*(columbia|barnard)\.edu$"

@app.route("/login", methods = ['GET', 'POST'])
def login():
    """
    Returns an auth code after user logs in through Google+.
    :param string code: code that is passed in through Google+.
        Do not provide this yourself.
    :return: An html page with an auth code.
    :rtype: flask.Response
    """
    # Get code from params.
    code = request.args.get('code')
    if not code:
        return render_template('auth.html',
                               success=False)
    print code
    try:
    # Exchange code for email address.
    # Get Google+ ID.
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        gplus_id = credentials.id_token['sub']

        # Get first email address from Google+ ID.
        http = httplib2.Http()
        http = credentials.authorize(http)

        h, content = http.request('https://www.googleapis.com/plus/v1/people/' + gplus_id, 'GET')
        data = json.loads(content)
        email = data["emails"][0]["value"]
        
        # Verify email is valid.
        regex = re.match(CU_EMAIL_REGEX, email)

        if not regex:
            return render_template('auth.html',
                                   success=False,
                                   reason="You need to log in with your "
                                   + "Columbia or Barnard email! You logged "
                                   + "in with: "
                                   + email)

        # Get UNI and ask database for code.
        uni = regex.group('uni')
        return render_template('auth.html', success=True, uni=uni, code=code)
    except Exception as e:
        # TODO: log errors3
        print e
        return render_template('auth.html',
                               success=False,
                               reason="An error occurred. Please try again.")

if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SECRET_KEY'] = 'secret key'
    sess.init_app(app)
    app.run(host = '0.0.0.0')