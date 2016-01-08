# Runs Flask Application for Giftie Web App
# written by jennifer lyden for Udacity FullStack Nanodegree

from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine, literal
from sqlalchemy.orm import sessionmaker
import datetime, random, string, httplib2, json, requests
from datetime import date, timedelta
from giftie_db import Base, Givers, Recipients, Gifts


app = Flask(__name__)

engine = create_engine('sqlite:///giftie.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

# Uncomment below when security added
#                    filter(giver.id = login_session['giver_id']).\
@app.route('/recipients')
def recipients():
    items = session.query(Recipients).\
                    order_by(Recipients.name).all()
    if not items:
        return render_template('recipientsNo.html')
    else:
        return render_template('recipientsYes.html', recipients = items)

# Uncomment below when security added
# giver_id=login_session['user_id']
@app.route('/recipients/add', methods=['GET', 'POST'])
def addRecipient():
    if request.method == 'POST':
        newRecipient = Recipients(name = request.form['name'],
                        bday = request.form['bday'],
                        sizes = request.form['sizes'])
        session.add(newRecipient)
        session.commit()
        flash("New recipient added!")
        return redirect(url_for('recipients'))
    else:
        return render_template('recipientAdd.html')

@app.route('/recipients/<int:rec_id>/edit', methods = ['GET', 'POST'])
def editRecipient(rec_id):
    thisRecipient = session.query(Recipients).\
                        filter_by(id = rec_id).one()
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
        return render_template('recipientEdit.html', recipient = thisRecipient, rec_id = rec_id)

@app.route('/recipients/<int:rec_id>/delete', methods=['GET', 'POST'])
def deleteRecipient(rec_id):
    thisRecipient = session.query(Recipients).\
                        filter_by(id = rec_id).one()
    if request.method == 'POST':
        theirGifts = session.query(Gifts).\
                        filter_by(rec_id = rec_id).all()
        for g in theirGifts:
            session.delete(g)
        session.delete(thisRecipient)
        session.commit()
        flash("Recipient and gifts deleted!")
        return redirect(url_for('recipients'))
    else:
        return render_template('recipientDelete.html', recipient = thisRecipient)

@app.route('/recipients/<int:rec_id>/gifts')
def gifts(rec_id):
    thisRecipient = session.query(Recipients).\
                    filter_by(id = rec_id).one()
    items = session.query(Gifts).\
                    filter_by(rec_id = rec_id).\
                    order_by(Gifts.name).all()
    if not items:
        return render_template('giftsNo.html', recipient = thisRecipient)
    else:
        return render_template('giftsYes.html', recipient = thisRecipient, gifts = items)

# Uncomment below when security added
# giver_id=login_session['user_id']
@app.route('/recipients/<int:rec_id>/gifts/add', methods=['GET', 'POST'])
def addGift(rec_id):
    thisRecipient = session.query(Recipients).\
                        filter_by(id = rec_id).one()
    if request.method == 'POST':
        status = request.form['status']
        newGift = Gifts(name = request.form['name'],\
                        desc = request.form['desc'],\
                        link = request.form['linkBuy'],\
                        image = request.form['linkPic'],\
                        status = status,\
                        date_added = date.today(),\
                        rec_id = rec_id)
#        if status == 'given':
#            newGift.date_given = date.today()
        session.add(newGift)
        session.commit()
        flash("New gift added!")
        return redirect(url_for('gifts', rec_id = rec_id))
    else:
        return render_template('giftAdd.html', recipient = thisRecipient, rec_id = rec_id)

# Uncomment below when security added
# giver_id=login_session['user_id']
@app.route('/recipients/gifts/<int:gift_id>/regive', methods=['GET', 'POST'])
def regiveGift(gift_id):
    oldGift = session.query(Gifts).\
                        filter_by(id = gift_id).one()
    allRecipients = session.query(Recipients).\
                        order_by(Recipients.name).all()
    if request.method == 'POST':
        newRec = session.query(Recipients).\
                        filter_by(name = request.form['newRecipient']).one()
        newGift = Gifts(name = oldGift.name,\
                        desc = oldGift.desc,\
                        link = oldGift.link,\
                        image = oldGift.image,\
                        status = "idea",\
                        date_added = date.today(),\
                        rec_id = newRec.id)
#        if status == 'given':
#            newGift.date_given = date.today()
        session.add(newGift)
        session.commit()
        flash("Gift added for a new recipient!")
        return redirect(url_for('gifts', rec_id = newRec.id))
    else:
        return render_template('giftRegive.html', gift_id = gift_id, gift = oldGift, recipients = allRecipients)

@app.route('/recipients/<int:rec_id>/gifts/<int:gift_id>/status', methods = ['GET', 'POST'])
def statusGift(rec_id, gift_id):
    thisGift = session.query(Gifts).\
                    filter_by(id = gift_id).one()
    if request.method == 'POST':
        if request.form['status']:
            thisGift.status = request.form['status']
        session.add(thisGift)
        session.commit()
        flash("Gift status changed!")
        return redirect(url_for('gifts', rec_id = rec_id, gift_id = gift_id))
    else:
        return render_template('giftChangeStatus.html', gift = thisGift, rec_id = rec_id, gift_id = gift_id)

@app.route('/recipients/<int:rec_id>/gifts/<int:gift_id>/edit', methods = ['GET', 'POST'])
def editGift(rec_id, gift_id):
    thisGift = session.query(Gifts).\
                    filter_by(id = gift_id).one()
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
        session.add(thisGift)
        session.commit()
        flash("Gift information changed!")
        return redirect(url_for('gifts', rec_id = rec_id, gift_id = gift_id))
    else:
        return render_template('giftEdit.html', gift = thisGift, rec_id = rec_id, gift_id = gift_id)

@app.route('/recipients/<int:rec_id>/gifts/<int:gift_id>/delete', methods=['GET', 'POST'])
def deleteGift(rec_id, gift_id):
    thisRecipient = session.query(Recipients).\
                        filter_by(id = rec_id).one()
    thisGift = session.query(Gifts).\
                        filter_by(id = gift_id).one()
    if request.method == 'POST':
        session.delete(thisGift)
        session.commit()
        flash("Gift deleted!")
        return redirect(url_for('gifts'))
    else:
        return render_template('giftDelete.html', recipient = thisRecipient, gift = thisGift, rec_id = rec_id, gift_id = gift_id)


#Fake Gifts
#gifts = [{'id': '1', 'recipient_id':'1', 'name':'Fiorentina Scarf', 'description':'Oversized Plaid Scarf with Fringe', 'image':'http://cdn.saleoffaccessories.com/d1/fc/d1fc1373d0e5e01ae234dd2c222b4468/la-fiorentina-plush-plaid-fringe-scarf.jpg', 'link':'http://www.amazon.com/Fiorentina-Womens-Oversized-Plaid-Fringe/dp/B00TV4CF36/ref=sr_1_7', 'status': 'idea'}, {'id': '2', 'recipient_id':'1', 'name':"What to Expect When You're Expecting", 'description':"America's pregnancy bible", 'image':"https://upload.wikimedia.org/wikipedia/en/d/d6/What_to_Expect_When_You're_Expecting_Cover.jpg", 'link':'http://www.amazon.com/What-Expect-When-Youre-Expecting/dp/0761148574/ref=sr_1_1', 'status': 'idea'}, {'id': '3', 'recipient_id':'1', 'name':'Mama Bee Belly Butter', 'description':"Burt's Bees Belly Butter, 6.5 Ounce", 'image':'http://www.allbabyforbaby.com/image/cache/data/burts-bees/burts-bees-mama-bee-belly-butter-6-5-ounce-2-500x500.jpg', 'link':'http://www.amazon.com/gp/product/B00DM14TYC/ref=s9_simh_gw_p14_d0_i5', 'status': 'idea'}, {'id': '4', 'recipient_id':'1', 'name':'Total Body Pillow', 'description':'Supports hips, back, neck, and tummy', 'image':'http://s7d9.scene7.com/is/image/BedBathandBeyond/8000415038357p', 'link':'http://www.amazon.com/gp/product/B0000635WI/ref=s9_simh_gw_p121_d0_i3', 'status': 'idea'}, {'id': '5', 'recipient_id':'1', 'name':'Baby Sling Carrier', 'description':'For babies from birth to 35 lbs', 'image':'https://images-na.ssl-images-amazon.com/images/I/41QZfy9IkAL.jpg', 'link':'http://www.amazon.com/Original--Fashion-Comfortable-Innoo-Tech/dp/B0156HL9WE/ref=sr_1_4', 'status': 'idea'}]
#gift = {'id': '1', 'recipient_id':'1', 'name':'Fiorentina Scarf', 'description':'Oversized Plaid Scarf with Fringe', 'image':'http://cdn.saleoffaccessories.com/d1/fc/d1fc1373d0e5e01ae234dd2c222b4468/la-fiorentina-plush-plaid-fringe-scarf.jpg', 'link':'http://www.amazon.com/Fiorentina-Womens-Oversized-Plaid-Fringe/dp/B00TV4CF36/ref=sr_1_7', 'status': 'idea'}


if __name__ == '__main__':
    app.secret_key = 'sha7b0t_4eY'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
