from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session, g
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import User, Strategy, Tactic, Base
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from uuid import uuid4
import httplib2
import json
from flask import make_response
import requests
from flask_oauthlib.client import OAuth



oauth = OAuth()

app = Flask(__name__)
app.debug = True
app.secret_key = 'development'



oauth = OAuth(app)

twitter = oauth.remote_app(
    'twitter',
    consumer_key='01FydfAxogRCXMBoqeGu2Vft8',
    consumer_secret='x2cFDgKeEpFarvrLoyoGgVmr7IqvGdi7ioXgw3YOlbL1NfpGJf',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize'
)


@twitter.tokengetter
def get_twitter_token():
    if 'twitter_oauth' in session:
        resp = session['twitter_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']


@app.before_request
def before_request():
    g.user = None
    if 'twitter_oauth' in session:
        g.user = session['twitter_oauth']


@app.route('/')
def index():
    tweets = None
    if g.user is not None:
        resp = twitter.request('statuses/home_timeline.json')
        if resp.status == 200:
            tweets = resp.data
        else:
            flash('Unable to load tweets from Twitter.')
    return render_template('index.html', tweets=tweets)

# @app.route('/')
# def index():
#     tweets = None
#     if g.user is not None:
#         resp = twitter.request('statuses/home_timeline.json')
#         if resp.status == 200:
#             tweets = resp.data
#         else:
#             flash('Unable to load tweets from Twitter.')
#     return render_template('index.html', tweets=tweets)

@app.route('/tweet', methods=['POST'])
def tweet():
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    status = request.form['tweet']
    if not status:
        return redirect(url_for('index'))
    resp = twitter.post('statuses/update.json', data={
        'status': status
    })

    if resp.status == 403:
        flash("Error: #%d, %s " % (
            resp.data.get('errors')[0].get('code'),
            resp.data.get('errors')[0].get('message'))
        )
    elif resp.status == 401:
        flash('Authorization error with Twitter.')
    else:
        flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
    return redirect(url_for('index'))


@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return redirect(url_for('index'))


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
    return redirect(url_for('showStrategies'))
# Login

# facebook = oauth.remote_app('facebook',
#     base_url='https://graph.facebook.com/',
#     request_token_url=None,
#     access_token_url='/oauth/access_token',
#     authorize_url='https://www.facebook.com/dialog/oauth',
#     consumer_key=181379492379757,
#     consumer_secret=be1e04fbacdd9d50a7dfbaabf29d95aa,
#     request_token_params={'scope': 'email'}
# )


# @app.route('/fbconnect', methods=['POST'])
# def fbconnect():
#     if request.args.get('state') != login_session['state']:
#         response = make_response(json.dumps('Invalid state parameter.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     access_token = request.data
#     print "access token received %s " % access_token

#         # Exchange client token for long-lived server-side token
#     fb_client_secrets_file = (app.config['OAUTH_SECRETS_LOCATION'] +
#                               'fb_client_secrets.json')
#     app_id = json.loads(
#         open(fb_client_secrets_file, 'r').read())['web']['app_id']
#     app_secret = json.loads(
#         open(fb_client_secrets_file, 'r').read())['web']['app_secret']
#     url = ('https://graph.facebook.com/v2.8/oauth/access_token?'
#            'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
#            '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
#     http = httplib2.Http()
#     result = http.request(url, 'GET')[1]
#     data = json.loads(result)

#     # Extract the access token from response
#     token = 'access_token=' + data['access_token']

#     # Use token to get user info from API.
#     url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' % token
#     http = httplib2.Http()
#     result = http.request(url, 'GET')[1]
#     data = json.loads(result)
#     login_session['provider'] = 'facebook'
#     login_session['username'] = data["name"]
#     login_session['email'] = data["email"]
#     login_session['facebook_id'] = data["id"]

#     # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
#     data = json.loads(result)
#     token = 'access_token=' + data['access_token']
#     login_session['access_token'] = stored_token

#     # Get user picture
#     url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[1]
#     data = json.loads(result)

#     login_session['picture'] = data["data"]["url"]

#     # see if user exists
#     user_id = getUserID(login_session['email'])
#     if not user_id:
#         user_id = createUser(login_session)
#     login_session['user_id'] = user_id

#     output = ''
#     output += '<h1>Welcome, '
#     output += login_session['username']

#     output += '!</h1>'
#     output += '<img src="'
#     output += login_session['picture']
#     output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

#     flash("Now logged in as %s" % login_session['username'])
#     return output


# @app.route('/fbdisconnect')
# def fbdisconnect():
#     facebook_id = login_session['facebook_id']
#     # The access token must me included to successfully logout
#     access_token = login_session['access_token']
#     url = ('https://graph.facebook.com/oauth/access_token?'
#            'grant_type=fb_exchange_token&client_id=%s&client_secret=%s'
#            '&fb_exchange_token=%s') % (app_id, app_secret, access_token)
#     h = httplib2.Http()
#     result = h.request(url, 'DELETE')[1]
#     return "you have been logged out"

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = db_session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


# @app.route('/gdisconnect')
# def gdisconnect():
#     # Only disconnect a connected user.
#     credentials = login_session.get('credentials')
#     if credentials is None:
#         response = make_response(
#             json.dumps('Current user not connected.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     access_token = credentials.access_token
#     url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[0]
#     if result['status'] != '200':
#         # For whatever reason, the given token was invalid.
#         response = make_response(
#             json.dumps('Failed to revoke token for given user.'), 400)
#         response.headers['Content-Type'] = 'application/json'
#         return response


# Connect to Database and create database session
engine = create_engine('sqlite:///strategytactic.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# make some JSON endpoints
@app.route('/strategy/<int:strategy_id>/tactic/JSON')
def strategyTacticJSON(strategy_id):
    strategy = db_session.query(Strategy).filter_by(id=strategy_id).one()
    tactics = db_session.query(Tactic).filter_by(
        strategy_id=strategy_id).all()
    return jsonify(Tactics=[t.serialize for t in tactics])


@app.route('/strategy/<int:strategy_id>/tactic/<int:tactic_id>/JSON')
def tacticJSON(strategy_id, tactic_id):
    Tactic = db_session.query(Tactic).filter_by(id=tactic_id).one()
    return jsonify(Tactic=Tactic.serialize)


@app.route('/strategy/JSON')
def strategiesJSON():
    strategies = db_session.query(Strategy).all()
    return jsonify(strategies=[s.serialize for s in strategies])

# Show all restaurants
@app.route('/')
@app.route('/strategies/')
def showStrategies():
    strategies = db_session.query(Strategy).order_by(asc(Strategy.name))
    # if 'username' not in login_session:
    #     return render_template('publicrestaurants.html', restaurants=restaurants)
    # else:
    return render_template('strategies.html', strategies=strategies)

@app.route('/pickStrategy')
def pickStrategy():
    strategies = db_session.query(Strategy).order_by(asc(Strategy.name))
    # if 'username' not in login_session:
    #     return render_template('publicrestaurants.html', restaurants=restaurants)
    # else:
    return render_template('pickStrategy.html', strategies=strategies)

# Create a new strategy
@app.route('/strategy/new/', methods=['GET', 'POST'])
def newStrategy():
    if request.method == 'POST':
        newStrategy = Strategy(name=request.form['name'])
        db_session.add(newStrategy)
        flash('New Strategy %s Successfully Created' % newStrategy.name)
        db_session.commit()
        return redirect(url_for('showStrategies'))
    else:
        return render_template('newStrategy.html')


# Edit a restaurant
@app.route('/strategy/<int:strategy_id>/edit/', methods=['GET', 'POST'])
def editStrategy(strategy_id):
    editedStrategy = db_session.query(
        Strategy).filter_by(id=strategy_id).one()
    # if 'username' not in login_session:
    #     return redirect('/login')
    # if editedStrategy.user_id != login_session['user_id']:
    #     return "<script>function myFunction() {alert('You are not authorized to edit this strategy. Please create your own restaurant in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedStrategy.name = request.form['name']
            flash('Successfully Edited %s' % editedStrategy.name)
            return redirect(url_for('showStrategies'))
    else:
        return render_template('editStrategy.html', strategy=editedStrategy)


# Delete a restaurant
@app.route('/strategy/<int:strategy_id>/delete/', methods=['GET', 'POST'])
def deleteStrategy(strategy_id):
    strategyToDelete = db_session.query(
        Strategy).filter_by(id=strategy_id).one()
    # if 'username' not in login_session:
    #     return redirect('/login')
    # if strategyToDelete.user_id != login_session['user_id']:
    #     return "<script>function myFunction() {alert('You are not authorized to delete this strategy. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        db_session.delete(strategyToDelete)
        flash('%s Successfully Deleted' % strategyToDelete.name)
        db_session.commit()
        return redirect(url_for('showStrategies', strategy_id=strategy_id))
    else:
        return render_template('deleteStrategy.html', strategy=strategyToDelete)


# #######
# TACTICS
# ########

# show tactics matching the strategy
@app.route('/strategy/<int:strategy_id>/')
@app.route('/strategy/<int:strategy_id>/tactic/')
def showTactic(strategy_id):
    strategy = db_session.query(Strategy).filter_by(id=strategy_id).one()
    # creator = getUserInfo(strategy.user_id)
    tactics = db_session.query(Tactic).filter_by(
        strategy_id=strategy_id).all()
    # if 'username' not in login_session or creator.id != login_session['user_id']:
    #     return render_template('publicmenu.html', tactics=tactics, strategy=strategy, creator=creator)
    # else:
    return render_template('tactic.html', tactics=tactics, strategy=strategy)


# Create a new tactic
@app.route('/strategy/<int:strategy_id>/tactic/new/', methods=['GET', 'POST'])
def newTactic(strategy_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    strategy = db_session.query(Strategy).filter_by(id=strategy_id).one()
    # if login_session['user_id'] != strategy.user_id:
    #     return "<script>function myFunction() {alert('You are not authorized to add tactics to this strategy. Please create your own restaurant in order to add items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        newTactic = Tactic(name=request.form['name'],
            description=request.form['description'],
            difficulty=request.form['difficulty'],
            resource_link=request.form['resource_link'],
            tool_link=request.form['tool_link'],
            strategy_id=strategy_id)
        # later add user_id=strategy.user_id above
        db_session.add(newTactic)
        db_session.commit()
        flash('New Tactic: %s  Successfully Created' % (newTactic.name))
        return redirect(url_for('showTactic', strategy_id=strategy_id))
    else:
        return render_template('newTactic.html', strategy_id=strategy_id, strategy=strategy)

# Edit a menu item
@app.route('/strategy/<int:strategy_id>/tactic/<int:tactic_id>/edit', methods=['GET', 'POST'])
def editTactic(strategy_id, tactic_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    editedTactic = db_session.query(Tactic).filter_by(id=tactic_id).one()
    strategy = db_session.query(Strategy).filter_by(id=strategy_id).one()
    # if login_session['user_id'] != strategy.user_id:
    #     return "<script>function myFunction() {alert('You are not authorized to edit tactics to this strategy. Please create your own strategy in order to edit items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedTactic.name = request.form['name']
        if request.form['description']:
            editedTactic.description = request.form['description']
        if request.form['difficulty']:
            editedTactic.difficulty = request.form['difficulty']
        if request.form['resource_link']:
            editedTactic.resource_link = request.form['resource_link']
        if request.form['tool_link']:
            editedTactic.tool_link = request.form['tool_link']

        db_session.add(editedTactic)
        db_session.commit()

        flash('Tactic Successfully Edited')
        return redirect(url_for('showTactic', strategy_id=strategy_id))
    else:
        return render_template('editTactic.html', strategy_id=strategy_id, tactic_id=tactic_id, tactic=editedTactic)


# Delete a menu item
@app.route('/strategy/<int:strategy_id>/tactic/<int:tactic_id>/delete', methods=['GET', 'POST'])
def deleteTactic(strategy_id, tactic_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    strategy = db_session.query(Strategy).filter_by(id=strategy_id).one()
    itemToDelete = db_session.query(Tactic).filter_by(id=tactic_id).one()
    # if login_session['user_id'] != strategy.user_id:
    #     return "<script>function myFunction() {alert('You are not authorized to delete tactics in this strategy. Please create your own strategy in order to delete tactics.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        db_session.delete(itemToDelete)
        db_session.commit()
        flash('Tactic Successfully Deleted')
        return redirect(url_for('showTactic', strategy_id=strategy_id))
    else:
        return render_template('deleteTactic.html', tactic=itemToDelete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)    

