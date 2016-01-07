# Runs Flask Application for Giftie Webpages
# written by jennifer lyden for Udacity FullStack Nanodegree

from flask import Flask, render_template, url_for, request, redirect, flash, jsonify, make_response


app = Flask(__name__)


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

@app.route('/recipients')
def recipients():
#    return 'Recipients listing'
    return render_template('recipients.html', recipients = recipients)

@app.route('/recipients/add')
def addRecipient():
    return 'Add a recipient'
#    return render_template('recipientAdd.html')

@app.route('/recipients/rec_id/edit')
def editRecipient():
    return 'Edit recipient with rec_id'
#    return render_template('recipientEdit.html', recipient = recipient)

@app.route('/recipients/rec_id/delete')
def deleteRecipient():
    return 'Delete recipient with rec_id'
#    return render_template('recipientDelete.html', recipient = recipient)

@app.route('/recipients/rec_id/gifts')
def gifts():
    return 'Gifts listing for recipient with rec_id'
#    return render_template('gifts.html', recipient = recipient, gifts = gifts)

@app.route('/recipients/rec_id/gifts/add')
def addGift():
    return 'Add gift for recipient with rec_id'
#    return render_template('giftAdd.html', recipient = recipient)

@app.route('/recipients/rec_id/gifts/gift_id/status')
def statusGift():
    return 'Change status of gift with gift_id for recipient with rec_id'
#    return render_template('giftChangeStatus.html', recipient = recipient, gift = gift)

@app.route('/recipients/rec_id/gifts/gift_id/edit')
def editGift():
    return 'Edit gift with gift_id status for recipient with rec_id'
#    return render_template('giftEdit.html', recipient = recipient, gift = gift)

@app.route('/recipients/rec_id/gifts/gift_id/delete')
def deleteGift():
    return 'Delete gift with gift_id status for recipient with rec_id'
#    return render_template('giftDelete.html', recipient = recipient, gift = gift)


#Fake Recipients
recipient = {'id':'1', 'name':'Susan Whitaker', 'bday':'Jan 2', 'sizes':'small'}
recipients = [{'id':'1', 'name':'Susan Whitaker', 'bday':'Jan 2', 'sizes':'small'}, {'id':'2', 'name':'Anne Lyden', 'bday':'Aug 30', 'sizes':'medium'}, {'id':'3', 'name':'Pepper Whitaker', 'bday':'Sept 2', 'sizes':'0-3 mo'}]

#Fake Gifts
gifts = [{'id': '1', 'recipient_id':'1', 'name':'Fiorentina Scarf', 'description':'Oversized Plaid Scarf with Fringe', 'image':'http://cdn.saleoffaccessories.com/d1/fc/d1fc1373d0e5e01ae234dd2c222b4468/la-fiorentina-plush-plaid-fringe-scarf.jpg', 'link':'http://www.amazon.com/Fiorentina-Womens-Oversized-Plaid-Fringe/dp/B00TV4CF36/ref=sr_1_7', 'status': 'idea'}, {'id': '2', 'recipient_id':'1', 'name':"What to Expect When You're Expecting", 'description':"America's pregnancy bible", 'image':"https://upload.wikimedia.org/wikipedia/en/d/d6/What_to_Expect_When_You're_Expecting_Cover.jpg", 'link':'http://www.amazon.com/What-Expect-When-Youre-Expecting/dp/0761148574/ref=sr_1_1', 'status': 'idea'}, {'id': '3', 'recipient_id':'1', 'name':'Mama Bee Belly Butter', 'description':"Burt's Bees Belly Butter, 6.5 Ounce", 'image':'http://www.allbabyforbaby.com/image/cache/data/burts-bees/burts-bees-mama-bee-belly-butter-6-5-ounce-2-500x500.jpg', 'link':'http://www.amazon.com/gp/product/B00DM14TYC/ref=s9_simh_gw_p14_d0_i5', 'status': 'idea'}, {'id': '4', 'recipient_id':'1', 'name':'Total Body Pillow', 'description':'Supports hips, back, neck, and tummy', 'image':'http://s7d9.scene7.com/is/image/BedBathandBeyond/8000415038357p', 'link':'http://www.amazon.com/gp/product/B0000635WI/ref=s9_simh_gw_p121_d0_i3', 'status': 'idea'}, {'id': '5', 'recipient_id':'1', 'name':'Baby Sling Carrier', 'description':'For babies from birth to 35 lbs', 'image':'https://images-na.ssl-images-amazon.com/images/I/41QZfy9IkAL.jpg', 'link':'http://www.amazon.com/Original--Fashion-Comfortable-Innoo-Tech/dp/B0156HL9WE/ref=sr_1_4', 'status': 'idea'}]
gift = {'id': '1', 'recipient_id':'1', 'name':'Fiorentina Scarf', 'description':'Oversized Plaid Scarf with Fringe', 'image':'http://cdn.saleoffaccessories.com/d1/fc/d1fc1373d0e5e01ae234dd2c222b4468/la-fiorentina-plush-plaid-fringe-scarf.jpg', 'link':'http://www.amazon.com/Fiorentina-Womens-Oversized-Plaid-Fringe/dp/B00TV4CF36/ref=sr_1_7', 'status': 'idea'}


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
