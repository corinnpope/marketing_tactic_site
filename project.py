import os
from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash, session, g
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


app = Flask(__name__)
app.debug = True
app.secret_key = 'development'


# setup oauth
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


# twitter methods
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


@app.route('/login')
def login():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


@app.route('/logout')
def logout():
    session.pop('twitter_oauth', None)
    return render_template('logout.html')


@app.route('/oauthorized')
def oauthorized():
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        session['twitter_oauth'] = resp
        access_token = resp['oauth_token']
        session['access_token'] = access_token
        session['screen_name'] = resp['screen_name']
        session['user_id'] = resp['user_id']
        session['twitter_token'] = (
            resp['oauth_token'],
            resp['oauth_token_secret'])
    return redirect(url_for('showStrategies'))


# Connect to Database and create database session
engine = create_engine('sqlite:///strategytactic.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


@app.route('/strategy/<int:strategy_id>/tactic/JSON')
def strategyTacticJSON(strategy_id):
    """  make some JSON endpoints for all the tactics in a strategy """
    strategy = db_session.query(Strategy).filter_by(id=strategy_id).one()
    tactics = db_session.query(Tactic).filter_by(
        strategy_id=strategy_id).all()
    return jsonify(Tactics=[t.serialize for t in tactics])


@app.route('/strategy/<int:strategy_id>/tactic/<int:tactic_id>/JSON')
def tacticJSON(strategy_id, tactic_id):
    """make JSON for each tactic"""
    Tactic = db_session.query(Tactic).filter_by(id=tactic_id).one()
    return jsonify(Tactic=Tactic.serialize)


@app.route('/strategy/JSON')
def strategiesJSON():
    """  make a JSON endpoint for each  """
    strategies = db_session.query(Strategy).all()
    return jsonify(strategies=[s.serialize for s in strategies])

# ############
# STRATEGIES #
# ############


@app.route('/')
@app.route('/strategies/')
def showStrategies():
    """ Show all strategies (visible to users & guests)"""
    strategies = db_session.query(Strategy).order_by(asc(Strategy.name))
    access_token = session.get('access_token')
    if access_token:
        access_token = access_token[0]
    return render_template('strategies.html', strategies=strategies)


@app.route('/pickStrategy')
def pickStrategy():
    """ if users click on create tactic from menu, first must pick a strategy """
    strategies = db_session.query(Strategy).order_by(asc(Strategy.name))
    return render_template('pickStrategy.html', strategies=strategies)


@app.route('/strategy/new/', methods=['GET', 'POST'])
def newStrategy():
    """ Create a new strategy (for logged in users only)"""
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    if request.method == 'POST':
        newStrategy = Strategy(
                                name=request.form['name'],
                                description=request.form['description'],
                                image=request.form['image'],
                                user_id=request.form['user_id']
                                )
        db_session.add(newStrategy)
        flash('New Strategy %s Successfully Created' % newStrategy.name)
        db_session.commit()
        return redirect(url_for('showStrategies'))
    else:
        return render_template('newStrategy.html')


@app.route('/strategy/<int:strategy_id>/edit/', methods=['GET', 'POST'])
def editStrategy(strategy_id):
    """Edit strategy"""
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    editedStrategy = db_session.query(
        Strategy).filter_by(id=strategy_id).one()
    if editedStrategy.user_id != session['screen_name']:
        # return a popup if user isn't strategy owner
        # broke line to be less than 78 characters, but now tabs are visible
        # in the alert box
        return "<script>function myFunction() {alert('You are not authorized\
        to edit this strategy. Please create your own strategy in order to\
        edit.'); window.location.href='/strategies';}</script> \
        <body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedStrategy.name = request.form['name']
        if request.form['description']:
            editedStrategy.description = request.form['description']
        if request.form['image']:
            editedStrategy.image = request.form['image']
        flash('Successfully Edited %s' % editedStrategy.name)
        return redirect(url_for('showStrategies'))
    else:
        return render_template('editStrategy.html', strategy=editedStrategy)


@app.route('/strategy/<int:strategy_id>/delete/', methods=['GET', 'POST'])
def deleteStrategy(strategy_id):
    """# Delete a strategy"""
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    strategyToDelete = db_session.query(
        Strategy).filter_by(id=strategy_id).one()
    if strategyToDelete.user_id != session['screen_name']:
        # unauthorized popup
        # broke line to be less than 78 characters, but now tabs are visible
        # in the alert box
        return "<script>function myFunction() {alert('You are not authorized\
        to delete this strategy. Please create your own strategy in order \
        to delete.'); window.location.href='/strategies';}</script> \
        <body onload='myFunction()''>"
    if request.method == 'POST':
        db_session.delete(strategyToDelete)
        flash('%s Successfully Deleted' % strategyToDelete.name)
        db_session.commit()
        return redirect(url_for('showStrategies', strategy_id=strategy_id))
    else:
        return render_template(
                                'deleteStrategy.html',
                                strategy=strategyToDelete
                                )


# #######
# TACTICS
# ########


@app.route('/strategy/<int:strategy_id>/')
@app.route('/strategy/<int:strategy_id>/tactic/')
def showTactic(strategy_id):
    """# show tactics matching the strategy"""
    strategy = db_session.query(Strategy).filter_by(id=strategy_id).one()
    tactics = db_session.query(Tactic).filter_by(
        strategy_id=strategy_id).all()
    return render_template(
                            'tactic.html',
                            tactics=tactics,
                            strategy=strategy,
                            strategy_id=strategy_id
                            )


@app.route('/strategy/<int:strategy_id>/tactic/<int:tactic_id>/details/')
def tacticDetails(strategy_id, tactic_id):
    """show details of a tactic"""
    # get the strategy it belongs to
    strategy = db_session.query(Strategy).filter_by(id=strategy_id).one()
    # find the tactic
    tactic = db_session.query(Tactic).filter_by(id=tactic_id).one()
    return render_template(
                            'tactic-detail.html',
                            strategy=strategy,
                            tactic=tactic
                            )


@app.route('/strategy/<int:strategy_id>/tactic/new/', methods=['GET', 'POST'])
def newTactic(strategy_id):
    """# Create a new tactic"""
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    strategy = db_session.query(Strategy).filter_by(id=strategy_id).one()
    # TODO - remove this part - there's no reason a user shouldn't be able to
    # create a new tactic for a strategy...
    if session['screen_name'] != strategy.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
            to add tactics to this strategy. Please create your own \
            strategy in order to add items.'); \
            window.location.href='/strategies';}</script> \
            <body onload='myFunction()''>"
    if request.method == 'POST':
        newTactic = Tactic(
                            name=request.form['name'],
                            description=request.form['description'],
                            difficulty=request.form['difficulty'],
                            resource_link=request.form['resource_link'],
                            tool_link=request.form['tool_link'],
                            strategy_id=strategy_id
                            )
        # later add user_id=strategy.user_id above
        db_session.add(newTactic)
        db_session.commit()
        flash('New Tactic: %s  Successfully Created' % (newTactic.name))
        return redirect(url_for('showTactic', strategy_id=strategy_id))
    else:
        return render_template(
                                'newTactic.html',
                                strategy_id=strategy_id,
                                strategy=strategy
                                )


@app.route(
            '/strategy/<int:strategy_id>/tactic/<int:tactic_id>/edit',
            methods=['GET', 'POST']
            )
def editTactic(strategy_id, tactic_id):
    """# Edit a tactic"""
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    editedTactic = db_session.query(Tactic).filter_by(id=tactic_id).one()
    strategy = db_session.query(Strategy).filter_by(id=strategy_id).one()
    # TODO - but you should only be able to edit/delete your own tactics ...
    # unless you're an admin which is a task for another day
    # change to tactic.user_id...
    if session['screen_name'] != strategy.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
        to edit tactics to this strategy. Please create your own strategy in \
        order to edit items.');window.location.href='/strategies';}</script> \
        <body onload='myFunction()''>"
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
        return render_template(
                                'editTactic.html',
                                strategy=strategy,
                                strategy_id=strategy_id,
                                tactic_id=tactic_id,
                                tactic=editedTactic
                                )


@app.route(
            '/strategy/<int:strategy_id>/tactic/<int:tactic_id>/delete',
            methods=['GET', 'POST']
            )
def deleteTactic(strategy_id, tactic_id):
    """# Delete a tactic"""
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    strategy = db_session.query(Strategy).filter_by(id=strategy_id).one()
    itemToDelete = db_session.query(Tactic).filter_by(id=tactic_id).one()
    if session['screen_name'] != strategy.user_id:
        return "<script>function myFunction() {alert('You are not authorized \
        to delete tactics in this strategy. Please create your own strategy in\
        order to delete tactics.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        db_session.delete(itemToDelete)
        db_session.commit()
        flash('Tactic Successfully Deleted')
        return redirect(url_for('showTactic', strategy_id=strategy_id))
    else:
        return render_template(
                                'deleteTactic.html',
                                strategy=strategy,
                                tactic=itemToDelete
                                )


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    # was app.run(host='0.0.0.0', port=5000)
    # changed for heroku deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)