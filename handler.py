# Runs Flask Application for Giftie Webpages
# written by jennifer lyden for Udacity FullStack Nanodegree

from flask import Flask
app = Flask(__name__)


@app.route('/')
@app.route('/welcome')
def welcome():
    return 'Welcome page'
#    return render_template('welcome.html')

@app.route('/login')
def login():
    return 'Login page'
#    return render_template('login.html')

@app.route('/register')
def register():
    return 'Registration page'
#    return render_template('register.html')

@app.route('/recipients')
def recipients():
    return 'Recipients listing'
#    return render_template('recipients.html', recipients = recipients)

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


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
