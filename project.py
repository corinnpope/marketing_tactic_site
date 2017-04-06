from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import User, Strategy, Tactic, Base
from flask import session as login_session
import random
import string
# from oauth2client.client import flow_from_clientsecrets
# from oauth2client.client import FlowExchangeError
# import httplib2
# import json
# from flask import make_response
# import requests

app = Flask(__name__)


# Connect to Database and create database session
engine = create_engine('sqlite:///strategytactic.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
# @app.route('/login')
# def showLogin():
#     state = ''.join(random.choice(string.ascii_uppercase + string.digits)
#                     for x in xrange(32))
#     login_session['state'] = state
#     # return "The current session state is %s" % login_session['state']
#     return render_template('login.html', STATE=state)


# @app.route('/fbconnect', methods=['POST'])
# def fbconnect():
#     if request.args.get('state') != login_session['state']:
#         response = make_response(json.dumps('Invalid state parameter.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     access_token = request.data
#     print "access token received %s " % access_token

#     app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
#         'web']['app_id']
#     app_secret = json.loads(
#         open('fb_client_secrets.json', 'r').read())['web']['app_secret']
#     url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
#         app_id, app_secret, access_token)
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[1]

#     # Use token to get user info from API
#     userinfo_url = "https://graph.facebook.com/v2.4/me"
#     # strip expire tag from access token
#     token = result.split("&")[0]


#     url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[1]
#     # print "url sent for API access:%s"% url
#     # print "API JSON result: %s" % result
#     data = json.loads(result)
#     login_session['provider'] = 'facebook'
#     login_session['username'] = data["name"]
#     login_session['email'] = data["email"]
#     login_session['facebook_id'] = data["id"]

#     # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
#     stored_token = token.split("=")[1]
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
#     url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
#     h = httplib2.Http()
#     result = h.request(url, 'DELETE')[1]
#     return "you have been logged out"


# @app.route('/gconnect', methods=['POST'])
# def gconnect():
#     # Validate state token
#     if request.args.get('state') != login_session['state']:
#         response = make_response(json.dumps('Invalid state parameter.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     # Obtain authorization code
#     code = request.data

#     try:
#         # Upgrade the authorization code into a credentials object
#         oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
#         oauth_flow.redirect_uri = 'postmessage'
#         credentials = oauth_flow.step2_exchange(code)
#     except FlowExchangeError:
#         response = make_response(
#             json.dumps('Failed to upgrade the authorization code.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response

#     # Check that the access token is valid.
#     access_token = credentials.access_token
#     url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
#            % access_token)
#     h = httplib2.Http()
#     result = json.loads(h.request(url, 'GET')[1])
#     # If there was an error in the access token info, abort.
#     if result.get('error') is not None:
#         response = make_response(json.dumps(result.get('error')), 500)
#         response.headers['Content-Type'] = 'application/json'
#         return response

#     # Verify that the access token is used for the intended user.
#     gplus_id = credentials.id_token['sub']
#     if result['user_id'] != gplus_id:
#         response = make_response(
#             json.dumps("Token's user ID doesn't match given user ID."), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response

#     # Verify that the access token is valid for this app.
#     if result['issued_to'] != CLIENT_ID:
#         response = make_response(
#             json.dumps("Token's client ID does not match app's."), 401)
#         print "Token's client ID does not match app's."
#         response.headers['Content-Type'] = 'application/json'
#         return response

#     stored_credentials = login_session.get('credentials')
#     stored_gplus_id = login_session.get('gplus_id')
#     if stored_credentials is not None and gplus_id == stored_gplus_id:
#         response = make_response(json.dumps('Current user is already connected.'),
#                                  200)
#         response.headers['Content-Type'] = 'application/json'
#         return response

#     # Store the access token in the session for later use.
#     login_session['access_token'] = credentials.access_token
#     login_session['gplus_id'] = gplus_id

#     # Get user info
#     userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
#     params = {'access_token': credentials.access_token, 'alt': 'json'}
#     answer = requests.get(userinfo_url, params=params)

#     data = answer.json()

#     login_session['username'] = data['name']
#     login_session['picture'] = data['picture']
#     login_session['email'] = data['email']
#     # ADD PROVIDER TO LOGIN SESSION
#     login_session['provider'] = 'google'

#     # see if user exists, if it doesn't make a new one
#     user_id = getUserID(data["email"])
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
#     flash("you are now logged in as %s" % login_session['username'])
#     print "done!"
#     return output

# # User Helper Functions


# def createUser(login_session):
#     newUser = User(name=login_session['username'], email=login_session[
#                    'email'], picture=login_session['picture'])
#     session.add(newUser)
#     session.commit()
#     user = session.query(User).filter_by(email=login_session['email']).one()
#     return user.id


# def getUserInfo(user_id):
#     user = session.query(User).filter_by(id=user_id).one()
#     return user


# def getUserID(email):
#     try:
#         user = session.query(User).filter_by(email=email).one()
#         return user.id
#     except:
#         return None

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


# JSON APIs to view Restaurant Information
# @app.route('/restaurant/<int:restaurant_id>/menu/JSON')
# def restaurantMenuJSON(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     items = session.query(MenuItem).filter_by(
#         restaurant_id=restaurant_id).all()
#     return jsonify(MenuItems=[i.serialize for i in items])


# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
# def menuItemJSON(restaurant_id, menu_id):
#     Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
#     return jsonify(Menu_Item=Menu_Item.serialize)


# @app.route('/restaurant/JSON')
# def restaurantsJSON():
#     restaurants = session.query(Restaurant).all()
#     return jsonify(restaurants=[r.serialize for r in restaurants])

# Show all restaurants
@app.route('/')
@app.route('/strategies/')
def showStrategies():
    strategies = session.query(Strategy).order_by(asc(Strategy.name))
    # if 'username' not in login_session:
    #     return render_template('publicrestaurants.html', restaurants=restaurants)
    # else:
    return render_template('strategies.html', strategies=strategies)

# Create a new restaurant


@app.route('/strategy/new/', methods=['GET', 'POST'])
def newStrategy():
    if request.method == 'POST':
        newStrategy = Strategy(name=request.form['name'])
        session.add(newStrategy)
        flash('New Strategy %s Successfully Created' % newStrategy.name)
        session.commit()
        return redirect(url_for('showStrategies'))
    else:
        return render_template('newStrategy.html')

# Edit a restaurant

@app.route('/strategy/<int:strategy_id>/edit/', methods=['GET', 'POST'])
def editStrategy(strategy_id):
    editedStrategy = session.query(
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
    strategyToDelete = session.query(
        Strategy).filter_by(id=strategy_id).one()
    # if 'username' not in login_session:
    #     return redirect('/login')
    # if strategyToDelete.user_id != login_session['user_id']:
    #     return "<script>function myFunction() {alert('You are not authorized to delete this strategy. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(strategyToDelete)
        flash('%s Successfully Deleted' % strategyToDelete.name)
        session.commit()
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
    strategy = session.query(Strategy).filter_by(id=strategy_id).one()
    # creator = getUserInfo(strategy.user_id)
    tactics = session.query(Tactic).filter_by(
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
    strategy = session.query(Strategy).filter_by(id=strategy_id).one()
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
        session.add(newTactic)
        session.commit()
        flash('New Tactic: %s  Successfully Created' % (newTactic.name))
        return redirect(url_for('showTactic', strategy_id=strategy_id))
    else:
        return render_template('newTactic.html', strategy_id=strategy_id, strategy=strategy)

# Edit a menu item
@app.route('/strategy/<int:strategy_id>/tactic/<int:tactic_id>/edit', methods=['GET', 'POST'])
def editTactic(strategy_id, tactic_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    editedTactic = session.query(Tactic).filter_by(id=tactic_id).one()
    strategy = session.query(Strategy).filter_by(id=strategy_id).one()
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

        session.add(editedTactic)
        session.commit()

        flash('Tactic Successfully Edited')
        return redirect(url_for('showTactic', strategy_id=strategy_id))
    else:
        return render_template('editTactic.html', strategy_id=strategy_id, tactic_id=tactic_id, tactic=editedTactic)


# Delete a menu item
@app.route('/strategy/<int:strategy_id>/tactic/<int:tactic_id>/delete', methods=['GET', 'POST'])
def deleteTactic(strategy_id, tactic_id):
    # if 'username' not in login_session:
    #     return redirect('/login')
    strategy = session.query(Strategy).filter_by(id=strategy_id).one()
    itemToDelete = session.query(Tactic).filter_by(id=tactic_id).one()
    # if login_session['user_id'] != strategy.user_id:
    #     return "<script>function myFunction() {alert('You are not authorized to delete tactics in this strategy. Please create your own strategy in order to delete tactics.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Tactic Successfully Deleted')
        return redirect(url_for('showTactic', strategy_id=strategy_id))
    else:
        return render_template('deleteTactic.html', tactic=itemToDelete)


# Disconnect based on provider
# @app.route('/disconnect')
# def disconnect():
#     if 'provider' in login_session:
#         if login_session['provider'] == 'google':
#             gdisconnect()
#             del login_session['gplus_id']
#             del login_session['credentials']
#         if login_session['provider'] == 'facebook':
#             fbdisconnect()
#             del login_session['facebook_id']
#         del login_session['username']
#         del login_session['email']
#         del login_session['picture']
#         del login_session['user_id']
#         del login_session['provider']
#         flash("You have successfully been logged out.")
#         return redirect(url_for('showRestaurants'))
#     else:
#         flash("You were not logged in")
#         return redirect(url_for('showRestaurants'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)    

