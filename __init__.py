# Runs Flask Application for Gifter Web App
# written by jennifer lyden for Udacity FullStack Nanodegree
#
# Errors in PEP8 check involve urls which break line length limits
# and indentation for session.query(), both of which I left for readability

from flask import Flask, render_template, url_for, request, redirect
from flask import flash, jsonify, make_response
from flask import session as login_session
from flask.ext.seasurf import SeaSurf
from sqlalchemy import create_engine, literal
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from xml.etree.ElementTree import Element, SubElement, Comment, tostring, dump
import os
import random
import string
import httplib2
import json
import requests
import datetime
from datetime import date
from functools import wraps
from gifter_db_setup import Base, Givers, Recipients, Gifts


app = Flask(__name__)
#app.config.from_object('config')

# For CSRF protection, from https://flask-seasurf.readthedocs.org/en/latest/
csrf = SeaSurf(app)

# Solving relative path issues
here = os.path.dirname(__file__)
client_secrets = os.path.join(here, 'client_secrets.json')
fb_client_secrets = os.path.join(here, 'fb_client_secrets.json')

# For Google authentication
CLIENT_ID = json.loads(
            open(client_secrets, 'r').read())['web']['client_id']
APPLICATION_NAME = "Gifter"

# Database connection setup
engine = create_engine('postgresql+psycopg2://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(function):
    """
    Check login status before continuing with function
    """
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if 'username' in login_session:
            return function(*args, **kwargs)
        else:
            flash('Sorry, you must login before proceeding.', 'alert-danger')
            return redirect(url_for('showLogin', next=request.url))
    return decorated_function


@app.route('/recipients/JSON')
def allRecipientsJSON():
    """
    Create JSON list of all recipients, with birthday, rec_id, name and sizes
    """
    items = session.query(Recipients).order_by(Recipients.id).all()
    return jsonify(AllRecipients=[i.serialize for i in items])


@app.route('/gifts/JSON')
def allGiftsJSON():
    """
    Create JSON list of all gifts, with description,
    gift_id, link, name and status
    """
    items = session.query(Gifts).order_by(Gifts.id).all()
    return jsonify(AllGifts=[i.serialize for i in items])


@app.route('/recipients/XML')
def allRecipientsXML():
    """
    Create XML list of all recipients, with birthday, rec_id, name and sizes

    .. note:: Helped by these websites -
        * https://discussions.udacity.com/t/create-an-additional-api-end-points-in-project-3/27060/3
        * http://stackoverflow.com/questions/29023035/how-to-create-xml-endpoint-in-flask
    """
    items = session.query(Recipients).order_by(Recipients.id).all()

    # Set up XML file
    recipientsXML = Element('allRecipients')
    comment = Comment('XML Response with all Recipients')
    recipientsXML.append(comment)
    title = SubElement(recipientsXML, 'title')
    title.text = 'Recipients List'

    # Fill with recipient data
    for i in items:
        thisRecipient = SubElement(recipientsXML, 'thisRecipient')
        thisRecipient.text = i.name
        rec_ID = SubElement(thisRecipient, 'rec_ID')
        rec_ID.text = str(i.id)
        bday = SubElement(thisRecipient, 'bday')
        bday.text = i.bday
        sizes = SubElement(thisRecipient, 'sizes')
        sizes.text = i.sizes
    return app.response_class(tostring(recipientsXML),
                              mimetype='application/xml')


@app.route('/gifts/XML')
def allGiftsXML():
    """
    Create XML list of all gifts, with description,
    gift_id, link, name and status
    """
    items = session.query(Gifts).order_by(Gifts.id).all()

    # Set up XML file
    giftsXML = Element('allGifts')
    comment = Comment('XML Response with all Gifts')
    giftsXML.append(comment)
    title = SubElement(giftsXML, 'title')
    title.text = 'Gifts List'

    # Fill with gift data
    for i in items:
        thisGift = SubElement(giftsXML, 'thisGift')
        thisGift.text = i.name
        gift_ID = SubElement(thisGift, 'gift_ID')
        gift_ID.text = str(i.id)
        desc = SubElement(thisGift, 'desc')
        desc.text = i.desc
        link = SubElement(thisGift, 'link')
        link.text = i.link
        status = SubElement(thisGift, 'status')
        status.text = i.status
    return app.response_class(tostring(giftsXML), mimetype='application/xml')


@app.route('/')
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login')
def showLogin():
    """
    Generate state token to prevent request forgery,
    then direct to login page
    """
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/register')
@csrf.exempt
def showRegister():
    """
    Generate state token to prevent request forgery,
    then direct to login page

    ..note:: Separate from normal login to clarify
    that logging in with a provider creates local account
    """
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('register.html')


@app.route('/gconnect', methods=['POST'])
@csrf.exempt
def gconnect():
    """
    Log in user through Google+
    """
    # check state token
    if request.args.get('state') != login_session['state']:
        connectMessage('Invalid state parameter', 401)
    code = request.data

    # Upgrade auth code into credentials object
    try:
        oauth_flow = flow_from_clientsecrets(client_secrets, scope='')
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

    # Set login_session data
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
    output += '<p>Ahoy '
    output += login_session['username']
    output += '.</p>'
    flash("You are now logged in as %s" % login_session['username'],
          'alert-info')
    print "Login complete!"
    return output


@app.route('/fbconnect', methods=['POST'])
@csrf.exempt
def fbconnect():
    """
    Log in user through Facebook
    """
    # check state token
    if request.args.get('state') != login_session['state']:
        connectMessage('Invalid state parameter', 401)
    access_token = request.data

    # Exchange client token for long-lived server-side token
    app_id = json.loads(
             open(fb_client_secrets, 'r').read())['web']['app_id']
    app_secret = json.loads(
             open(fb_client_secrets, 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # User token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # Strip expire tag from access token
    token = result.split("&")[0]

    # Get user info
    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    # Set login_session data
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
    output += '<p>Ahoy '
    output += login_session['username']
    output += '.</p>'
    flash("You are now logged in as %s" % login_session['username'],
          'alert-info')
    print "Login complete!"
    return output


@app.route('/disconnect')
def disconnect():
    """
    General logout/disconnect which invokes provider disconnects
    """
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
        flash("You have successfully logged out.", 'alert-info')
        return redirect(url_for('welcome'))
    else:
        flash("You were not logged in!", 'alert-info')
        return redirect(url_for('welcome'))


@app.route('/gdisconnect')
def gdisconnect():
    """
    Google disconnect - revoke user's token
    """
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


@app.route('/fbdisconnect')
def fbdisconnect():
    """
    Facebook disconnect
    """
    # Execute HTTP DELETE request to log out user
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been logged out."


# Four Login Helper functions
def connectMessage(message, code):
    """
    Render responses during log in process
    """
    response = make_response(json.dumps(message), code)
    response.headers['Content-Type'] = 'application/json'
    return response


def getGiverID(email):
    """
    Query giver (user) id based on e-mail address
    """
    try:
        thisGiver = session.query(Givers).filter_by(email=email).first()
        return thisGiver.id
    except:
        return None


def getGiverInfo(user_id):
    """
    Query giver (user) id based on giver id
    """
    thisGiver = session.query(Givers).filter_by(id=user_id).first()
    return thisGiver


def createGiver(login_session):
    """
    Create new giver (user) in database
    """
    newGiver = Givers(name=login_session['username'],
                      email=login_session['email'],
                      picture=login_session['picture'])
    session.add(newGiver)
    session.commit()
    user_id = getGiverID(login_session['email'])
    return user_id


@app.route('/demoLogin')
def demoLogin():
    """
    Fake "Login" for Demo User
    """
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state

    login_session['provider'] = 'demo'

    demoUser = session.query(Givers).\
                filter_by(name="Demo Giver").one()
    login_session['username'] = demoUser.name
    login_session['email'] = demoUser.email
    login_session['picture'] = demoUser.picture
    login_session['user_id'] = demoUser.id
    return render_template('demoUser.html')


@app.route('/recipients')
@login_required
def recipients():
    """
    Query user's (giver's) recipient list
    """
    items = session.query(Recipients).\
                filter_by(giver_id=login_session['user_id']).\
                order_by(Recipients.name).all()
    if not items:
        return render_template('recipientsNo.html')
    else:
        return render_template('recipientsYes.html', recipients=items)


@app.route('/recipients/add', methods=['GET', 'POST'])
@login_required
def addRecipient():
    """
    Create recipient in database
    """
    if request.method == 'POST':
        newRecipient = Recipients(name=request.form['name'],
                                  bday=request.form['bday'],
                                  sizes=request.form['sizes'],
                                  giver_id=login_session['user_id'])
        session.add(newRecipient)
        session.commit()
        flash("New recipient added!", 'alert-info')
        return redirect(url_for('recipients'))
    else:
        return render_template('recipientAdd.html')


@app.route('/recipients/<int:rec_id>/edit', methods=['GET', 'POST'])
@login_required
def editRecipient(rec_id):
    """
    Update recipient in database
    """
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()
    if not thisRecipient:
        flash('No such recipient!', 'alert-warning')
        return redirect(url_for('recipients'))

    # Authorization
    if thisRecipient.giver_id != login_session['user_id']:
        flash('Sorry, you are not authorized to edit this recipient.',
              'alert-danger')
        return redirect(url_for('recipients'))

    # Update data as provided
    if request.method == 'POST':
        if request.form['name']:
            thisRecipient.name = request.form['name']
        if request.form['bday']:
            thisRecipient.bday = request.form['bday']
        if request.form['sizes']:
            thisRecipient.sizes = request.form['sizes']
        session.add(thisRecipient)
        session.commit()
        flash("Recipient information changed!", 'alert-info')
        return redirect(url_for('recipients'))
    else:
        return render_template('recipientEdit.html',
                               recipient=thisRecipient, rec_id=rec_id)


@app.route('/recipients/<int:rec_id>/delete', methods=['GET', 'POST'])
@login_required
def deleteRecipient(rec_id):
    """
    Delete recipient & associated gifts from database
    """
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()
    if not thisRecipient:
        flash('No such recipient!', 'alert-warning')
        return redirect(url_for('recipients'))

    # Authorization
    if thisRecipient.giver_id != login_session['user_id']:
        flash('Sorry, you are not authorized to delete this recipient.',
              'alert-danger')
        return redirect(url_for('recipients'))

    # Delete recipient and associated gifts
    if request.method == 'POST':
        session.delete(thisRecipient)
        session.commit()
        flash("Recipient and gifts deleted!", 'alert-info')
        return redirect(url_for('recipients'))
    else:
        return render_template('recipientDelete.html',
                               recipient=thisRecipient)


@app.route('/gifts')
@login_required
def allGifts():
    """
    Query all gifts in database
    """
    items = session.query(Gifts).\
                order_by(Gifts.id).all()
    if not items:
        return render_template('giftsNo.html')
    else:
        return render_template('giftsAll.html', gifts=items)


@app.route('/recipients/gifts')
@login_required
def allYourGifts():
    """
    Query all gifts for logged-in giver (user) from database
    """
    items = session.query(Gifts).\
                filter_by(giver_id=login_session['user_id']).\
                order_by(Gifts.rec_id).all()
    if not items:
        return render_template('giftsNoneYour.html')
    else:
        return render_template('giftsAllYour.html', gifts=items)


@app.route('/recipients/<int:rec_id>/gifts')
@login_required
def gifts(rec_id):
    """
    Query all gifts for particular recipient from logged-in giver (user)
    """
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()
    if not thisRecipient:
        flash('No such recipient!', 'alert-warning')
        return redirect(url_for('recipients'))
    items = session.query(Gifts).\
                filter_by(rec_id=rec_id).\
                order_by(Gifts.name).all()
    if not items:
        return render_template('giftsNoneYour.html', recipient=thisRecipient,
                               rec_id=rec_id)
    else:
        return render_template('giftsYes.html',
                               recipient=thisRecipient, gifts=items,
                               rec_id=rec_id)


@app.route('/recipients/<int:rec_id>/gifts/<int:gift_id>')
@login_required
def giftDetails(rec_id, gift_id):
    """
    Query particular gift and show its details
    """
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()
    if not thisRecipient:
        flash('No such recipient!', 'alert-warning')
        return redirect(url_for('recipients'))
    thisGift = session.query(Gifts).\
                    filter_by(id=gift_id).first()
    if not thisGift:
        flash('No such gift!', 'alert-warning')
        return redirect(url_for('gifts'))
    return render_template('giftDetails.html',
                           rec_id=rec_id, gift_id=gift_id,
                           recipient=thisRecipient, gift=thisGift)


@app.route('/recipients/gifts/pick', methods=['GET', 'POST'])
@login_required
def pickRec():
    """
    Select recipient who will receive gift
    """
    if request.method == 'POST':
        newRec = session.query(Recipients).\
                        filter_by(name=request.form['newRecipient']).first()
        return redirect(url_for('addGift', rec_id=newRec.id))
    else:
        # Query available recipients
        giver_id = login_session['user_id']
        allRecipients = session.query(Recipients).\
                            filter_by(giver_id=giver_id).\
                            order_by(Recipients.name).all()
        if not allRecipients:
            flash('You must have a recipient before you can add a gift.',
                  'alert-warning')
            return redirect(url_for('addRecipient'))
        return render_template('recipientPick.html',
                               giver_id=giver_id, recipients=allRecipients)


@app.route('/recipients/<int:rec_id>/gifts/add', methods=['GET', 'POST'])
@login_required
def addGift(rec_id):
    """
    Create gift listing in database associated with a particular recipient
    """
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()
    if not thisRecipient:
        flash('No such recipient!', 'alert-warning')
        return redirect(url_for('recipients'))

    # Authorization
    if thisRecipient.giver_id != login_session['user_id']:
        flash('''Sorry, you can't add a Gift for this recipient.''',
              'alert-danger')
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
        flash("New gift added!", 'alert-info')
        return redirect(url_for('gifts', rec_id=rec_id))
    else:
        return render_template('giftAdd.html',
                               recipient=thisRecipient, rec_id=rec_id)


@app.route('/recipients/gifts/<int:gift_id>/regive', methods=['GET', 'POST'])
@login_required
def regiveGift(gift_id):
    """
    Copy an already registered gift to a different recipient
    """
    oldGift = session.query(Gifts).\
                    filter_by(id=gift_id).first()
    if not oldGift:
        flash('No such gift!', 'alert-warning')
        return redirect(url_for('gifts'))

    # Query available recipients
    giver_id = login_session['user_id']
    allRecipients = session.query(Recipients).\
                        filter_by(giver_id=giver_id).\
                        order_by(Recipients.name).all()
    if not allRecipients:
        flash('You have no recipients.', 'alert-warning')
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
        flash("Gift added for a new recipient!", 'alert-info')
        return redirect(url_for('gifts', rec_id=newRec.id))
    else:
        return render_template('giftRegive.html',
                               gift_id=gift_id, gift=oldGift,
                               recipients=allRecipients)


@app.route('/recipients/<int:rec_id>/gifts/<int:gift_id>/status',
           methods=['GET', 'POST'])
@login_required
def statusGift(rec_id, gift_id):
    """
    Update status of gift in database

    ..note:: Separated from other gift updates for user ease
    """
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()

    # Authorization
    if thisRecipient.giver_id != login_session['user_id']:
        flash('Sorry, you are not authorized to edit this gift.',
              'alert-danger')
        return redirect(url_for('recipients'))

    # Update status
    thisGift = session.query(Gifts).\
                    filter_by(id=gift_id).first()
    if request.method == 'POST':
        if request.form['status']:
            thisGift.status = request.form['status']
            if thisGift.status == 'given':
                thisGift.date_given = date.today()
        session.add(thisGift)
        session.commit()
        flash("Gift status changed!", 'alert-info')
        return redirect(url_for('gifts', rec_id=rec_id, gift_id=gift_id))
    else:
        return render_template('giftChangeStatus.html',
                               gift=thisGift, rec_id=rec_id,
                               gift_id=gift_id)


@app.route('/recipients/<int:rec_id>/gifts/<int:gift_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editGift(rec_id, gift_id):
    """
    Update status of gift in database
    """
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()

    # Authorization
    if thisRecipient.giver_id != login_session['user_id']:
        flash('Sorry, you are not authorized to edit this gift.',
              'alert-danger')
        return redirect(url_for('recipients'))

    thisGift = session.query(Gifts).\
                    filter_by(id=gift_id).first()

    # Update data as provided
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
        flash("Gift information changed!", 'alert-info')
        return redirect(url_for('gifts', rec_id=rec_id, gift_id=gift_id))
    else:
        return render_template('giftEdit.html', gift=thisGift,
                               rec_id=rec_id, gift_id=gift_id)


@app.route('/recipients/<int:rec_id>/gifts/<int:gift_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteGift(rec_id, gift_id):
    """
    Delete gift from database
    """
    thisRecipient = session.query(Recipients).\
                        filter_by(id=rec_id).first()

    # Authorization
    if thisRecipient.giver_id != login_session['user_id']:
        flash('Sorry, you are not authorized to delete this gift.',
              'alert-danger')
        return redirect(url_for('recipients'))

    thisGift = session.query(Gifts).\
                    filter_by(id=gift_id).first()
    if request.method == 'POST':
        session.delete(thisGift)
        session.commit()
        flash("Gift deleted!", 'alert-info')
        return redirect(url_for('gifts', rec_id=rec_id))
    else:
        return render_template('giftDelete.html', recipient=thisRecipient,
                               gift=thisGift, rec_id=rec_id,
                               gift_id=gift_id)


if __name__ == '__main__':
    app.secret_key = 'sha7b0t_4eY'
    app.debug = True
    app.run()
