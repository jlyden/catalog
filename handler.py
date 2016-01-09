# Runs Flask Application for Gifter Web App
# written by jennifer lyden for Udacity FullStack Nanodegree

from flask import Flask, render_template, url_for, request, redirect
from flask import flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine, literal
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import datetime, random, string, httplib2, json, requests
from datetime import date, timedelta
from gifter_db import Base, Givers, Recipients, Gifts


app = Flask(__name__)

# For Google authentication
CLIENT_ID = json.loads(
            open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Gifter"

# Database connection setup
engine = create_engine('sqlite:///gifter.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# API Endpoint - JSON
@app.route('/recipients/JSON')
def allRecipientsJSON():
    items = session.query(Recipients).order_by(Recipients.id).all()
    return jsonify(AllRecipients=[i.serialize for i in items])


@app.route('/gifts/JSON')
def allGiftsJSON():
    items = session.query(Gifts).order_by(Gifts.id).all()
    return jsonify(AllGifts=[i.serialize for i in items])


@app.route('/')
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


# State token to prevent request forgery
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/register')
def showRegister():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('register.html')


# Google Sign In functions
@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        connectMessage('Invalid state parameter', 401)
    code = request.data

    # Upgrade auth code into credentials object
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        connectMessage('Failed to upgrade the authorization code.', 401)

    # Check access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
            % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was error in access token info, abort
    if result.get('error') is not None:
        connectMessage(result.get('error'), 500)

    # Verify intended user presented access token
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        connectMessage("Token's user ID doesn't match given user ID.", 401)

    # Verify access token valid for this app
    if result['issued_to'] != '906905857159-19l8lcp90j3utgq2itj4upgdjtjaaltm.apps.googleusercontent.com':
        connectMessage("Token's client ID doesn't match app's.", 401)

    # If pass above tests ...
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        connectMessage('Current user is already connected.', 200)

    # Store access token in session for later use
    login_session['credentials'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['picture'] = data['picture']

    # Check if user exists in Database
    email = login_session['email']
    user_id = getGiverID(email)
    if not user_id:
        user_id = createGiver(login_session)
    login_session['user_id'] = user_id

    # Respond to user
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 150px; height 150px; border-radius: 75px;'
    output += ' -webkit-border-radius: 75px; -moz-border-radius: 75px;">'
    flash("You are now logged in as %s" % login_session['username'])
    print "Login complete!"
    return output


# Google disconnect - revoke user's token
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    access_token = login_session.get('credentials')
    if access_token is None:
        connectMessage('User not connected.', 401)
    # Execute HTTP GET request to revoke token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        connectMessage('Successfully disconnected.', 200)
    else:
        # For some reason, token was invalid
        connectMessage('Failed to revoke token for given user.', 400)


# Facebook connect
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        connectMessage('Invalid state parameter', 401)
    access_token = request.data

    # Exchange client token for long-lived server-side token
    app_id = json.loads(
             open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
             open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # User token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # Strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    # Store access token for later logout
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=150&width=150' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['picture'] = data['data']['url']

    # Check if user exists in database
    user_id = getGiverID(login_session['email'])
    if not user_id:
        user_id = createGiver(login_session)
    login_session['user_id'] = user_id

    # Respond to user
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 150px; height 150px; border-radius: 75px;'
    output += ' -webkit-border-radius: 75px; -moz-border-radius: 75px;">'
    flash("You are now logged in as %s" % login_session['username'])
    print "Login complete!"
    return output


# Facebook disconnect
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out."


# Super disconnect
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        # Call provider disconnect to revoke access token
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']

        # Finish reset of  login_session
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully logged out.")
        return redirect(url_for('welcome'))
    else:
        flash("You were not logged in!")
        return redirect(url_for('welcome'))


# Helper functions
def connectMessage(message, code):
        response = make_response(json.dumps(message), code)
        response.headers['Content-Type'] = 'application/json'
        return response


def getGiverID(email):
    try:
        thisGiver = session.query(Givers).filter_by(email=email).first()
        return thisGiver.id
    except:
        return None


def getGiverInfo(user_id):
    thisGiver = session.query(Givers).filter_by(id=user_id).first()
    return thisGiver


def createGiver(login_session):
    newGiver = Givers(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(newGiver)
    session.commit()
    user_id = getGiverID(login_session['email'])
    return user_id


# User's (Giver's) recipient list
@app.route('/recipients')
def recipients():
    if 'username' not in login_session:
        flash('Sorry, you must login before proceeding.')
        return redirect(url_for('welcome'))
    items = session.query(Recipients).\
                    filter_by(giver_id=login_session['user_id']).\
                    order_by(Recipients.name).all()
    if not items:
        return render_template('recipientsNo.html')
    else:
        return render_template('recipientsYes.html', recipients=items)


# Add recipient
@app.route('/recipients/add', methods=['GET', 'POST'])
def addRecipient():
    if 'username' not in login_session:
        flash('Sorry, you must login before proceeding.')
        return redirect(url_for('welcome'))
    if request.method == 'POST':
        newRecipient = Recipients(name=request.form['name'],
                        bday=request.form['bday'],
                        sizes=request.form['sizes'],
                        giver_id=login_session['user_id'])
        session.add(newRecipient)
        session.commit()
        flash("New recipient added!")
        return redirect(url_for('recipients'))
    else:
        return render_template('recipientAdd.html')


# Edit recipient
@app.route('/recipients/<int:rec_id>/edit', methods=['GET', 'POST'])
def editRecipient(rec_id):
    if 'username' not in login_session:
        flash('Sorry, you must login before proceeding.')
        return redirect(url_for('welcome'))
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()
    if not thisRecipient:
        flash('No such recipient!')
        return redirect(url_for('recipients'))
    if thisRecipient.giver_id != login_session['user_id']:
        flash('Sorry, you are not authorized to edit this recipient.')
        return redirect(url_for('recipients'))
    if request.method == 'POST':
        if request.form['name']:
            thisRecipient.name = request.form['name']
        if request.form['bday']:
            thisRecipient.bday = request.form['bday']
        if request.form['sizes']:
            thisRecipient.sizes = request.form['sizes']
        session.add(thisRecipient)
        session.commit()
        flash("Recipient information changed!")
        return redirect(url_for('recipients'))
    else:
        return render_template('recipientEdit.html',
                                recipient=thisRecipient, rec_id=rec_id)


# Delete recipient & recipient's gifts
@app.route('/recipients/<int:rec_id>/delete', methods=['GET', 'POST'])
def deleteRecipient(rec_id):
    if 'username' not in login_session:
        flash('Sorry, you must login before proceeding.')
        return redirect(url_for('welcome'))
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()
    if not thisRecipient:
        flash('No such recipient!')
        return redirect(url_for('recipients'))
    if thisRecipient.giver_id != login_session['user_id']:
        flash('Sorry, you are not authorized to delete this recipient.')
        return redirect(url_for('recipients'))
    if request.method == 'POST':
        theirGifts = session.query(Gifts).\
                        filter_by(rec_id=rec_id).all()
        for g in theirGifts:
            session.delete(g)
        session.delete(thisRecipient)
        session.commit()
        flash("Recipient and gifts deleted!")
        return redirect(url_for('recipients'))
    else:
        return render_template('recipientDelete.html',
                                recipient=thisRecipient)


# Gifts list associated with a particular recipient
@app.route('/recipients/<int:rec_id>/gifts')
def gifts(rec_id):
    if 'username' not in login_session:
        flash('Sorry, you must login before proceeding.')
        return redirect(url_for('welcome'))
    thisRecipient = session.query(Recipients).\
                    filter_by(id=rec_id).first()
    if not thisRecipient:
        flash('No such recipient!')
        return redirect(url_for('recipients'))
    items = session.query(Gifts).\
                    filter_by(rec_id=rec_id).\
                    order_by(Gifts.name).all()
    if not items:
        return render_template('giftsNo.html', recipient=thisRecipient)
    else:
        return render_template('giftsYes.html',
                                recipient=thisRecipient, gifts=items)


# See details about particular gift
@app.route('/recipients/<int:rec_id>/gifts/<int:gift_id>')
def giftDetails(rec_id, gift_id):
    if 'username' not in login_session:
        flash('Sorry, you must login before proceeding.')
        return redirect(url_for('welcome'))
    thisRecipient = session.query(Recipients).\
                    filter_by(id=rec_id).first()
    if not thisRecipient:
        flash('No such recipient!')
        return redirect(url_for('recipients'))
    thisGift = session.query(Gifts).\
                    filter_by(id=gift_id).first()
    if not thisGift:
        flash('No such gift!')
        return redirect(url_for('gifts'))
    return render_template('giftDetails.html',
                            recipient=thisRecipient, gift=thisGift)


# Add a gift for a particular recipient
@app.route('/recipients/<int:rec_id>/gifts/add', methods=['GET', 'POST'])
def addGift(rec_id):
    if 'username' not in login_session:
        flash('Sorry, you must login before proceeding.')
        return redirect(url_for('welcome'))
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()
    if not thisRecipient:
        flash('No such recipient!')
        return redirect(url_for('recipients'))
    if thisRecipient.giver_id != login_session['user_id']:
        flash('''Sorry, you can't add a Gift for this recipient.''')
        return redirect(url_for('recipients'))
    if request.method == 'POST':
        newGift = Gifts(name=request.form['name'],
                        desc=request.form['desc'],
                        link=request.form['linkBuy'],
                        image=request.form['linkPic'],
                        status=request.form['status'],
                        date_added=date.today(),
                        giver_id=login_session['user_id'],
                        rec_id=rec_id)
        if newGift.status == 'given':
            newGift.date_given = date.today()
        session.add(newGift)
        session.commit()
        flash("New gift added!")
        return redirect(url_for('gifts', rec_id=rec_id))
    else:
        return render_template('giftAdd.html',
                                recipient=thisRecipient, rec_id=rec_id)


# Copy an already registered gift to a different recipient
@app.route('/recipients/gifts/<int:gift_id>/regive', methods=['GET', 'POST'])
def regiveGift(gift_id):
    if 'username' not in login_session:
        flash('Sorry, you must login before proceeding.')
        return redirect(url_for('welcome'))
    oldGift = session.query(Gifts).\
                        filter_by(id=gift_id).first()
    if not oldGift:
        flash('No such gift!')
        return redirect(url_for('gifts'))
    giver_id = login_session['user_id']
    allRecipients = session.query(Recipients).\
                        filter_by(giver_id=giver_id).\
                        order_by(Recipients.name).all()
    if not allRecipients:
        flash('You have no recipients.')
        return redirect(url_for('recipients'))
    if request.method == 'POST':
        newRec = session.query(Recipients).\
                        filter_by(name=request.form['newRecipient']).first()
        newGift = Gifts(name=oldGift.name,
                        desc=oldGift.desc,
                        link=oldGift.link,
                        image=oldGift.image,
                        status="idea",
                        date_added=date.today(),
                        giver_id=login_session['user_id'],
                        rec_id=newRec.id)
        session.add(newGift)
        session.commit()
        flash("Gift added for a new recipient!")
        return redirect(url_for('gifts', rec_id=newRec.id))
    else:
        return render_template('giftRegive.html',
                                gift_id=gift_id, gift=oldGift,
                                recipients=allRecipients)


# Change gift's status
@app.route('/recipients/<int:rec_id>/gifts/<int:gift_id>/status',
            methods=['GET', 'POST'])
def statusGift(rec_id, gift_id):
    if 'username' not in login_session:
        flash('Sorry, you must login before proceeding.')
        return redirect(url_for('welcome'))
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()
    if thisRecipient.giver_id != login_session['user_id']:
        flash('Sorry, you are not authorized to edit this gift.')
        return redirect(url_for('recipients'))
    thisGift = session.query(Gifts).\
                    filter_by(id=gift_id).first()
    if request.method == 'POST':
        if request.form['status']:
            thisGift.status = request.form['status']
            if thisGift.status == 'given':
                thisGift.date_given = date.today()
        session.add(thisGift)
        session.commit()
        flash("Gift status changed!")
        return redirect(url_for('gifts', rec_id=rec_id, gift_id=gift_id))
    else:
        return render_template('giftChangeStatus.html',
                                gift=thisGift, rec_id=rec_id,
                                gift_id=gift_id)


# Edit gift's details
@app.route('/recipients/<int:rec_id>/gifts/<int:gift_id>/edit',
            methods=['GET', 'POST'])
def editGift(rec_id, gift_id):
    if 'username' not in login_session:
        flash('Sorry, you must login before proceeding.')
        return redirect(url_for('welcome'))
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()
    if thisRecipient.giver_id != login_session['user_id']:
        flash('Sorry, you are not authorized to edit this gift.')
        return redirect(url_for('recipients'))
    thisGift = session.query(Gifts).\
                    filter_by(id=gift_id).first()
    if request.method == 'POST':
        if request.form['name']:
            thisGift.name = request.form['name']
        if request.form['desc']:
            thisGift.desc = request.form['desc']
        if request.form['linkBuy']:
            thisGift.link = request.form['linkBuy']
        if request.form['linkPic']:
            thisGift.image = request.form['linkPic']
        if request.form['status']:
            thisGift.status = request.form['status']
            if thisGift.status == 'given':
                thisGift.date_given = date.today()
        session.add(thisGift)
        session.commit()
        flash("Gift information changed!")
        return redirect(url_for('gifts', rec_id=rec_id, gift_id=gift_id))
    else:
        return render_template('giftEdit.html', gift=thisGift,
                                rec_id=rec_id, gift_id=gift_id)


# Delete gift
@app.route('/recipients/<int:rec_id>/gifts/<int:gift_id>/delete',
            methods=['GET', 'POST'])
def deleteGift(rec_id, gift_id):
    if 'username' not in login_session:
        flash('Sorry, you must login before proceeding.')
        return redirect(url_for('welcome'))
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()
    if thisRecipient.giver_id != login_session['user_id']:
        flash('Sorry, you are not authorized to delete this gift.')
        return redirect(url_for('recipients'))
    thisGift = session.query(Gifts).\
                        filter_by(id=gift_id).first()
    if request.method == 'POST':
        session.delete(thisGift)
        session.commit()
        flash("Gift deleted!")
        return redirect(url_for('gifts'))
    else:
        return render_template('giftDelete.html', recipient=thisRecipient,
                                gift=thisGift, rec_id=rec_id,
                                gift_id=gift_id)


if __name__ == '__main__':
    app.secret_key = 'sha7b0t_4eY'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
