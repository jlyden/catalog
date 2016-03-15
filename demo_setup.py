# Sets up Demo User and Data for Gifter Web App
# written by jennifer lyden for Udacity FullStack Nanodegree
#
# Since this code is just loading demo data,
# I ignored long-line errors in PEP8 check


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import psycopg2
from gifter_db_setup import Base, Givers, Recipients, Gifts

# Database connection setup
engine = create_engine('postgresql+psycopg2://catalog:catalog@localhost/catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create Demo Giver & Other Giver
demoGiver = Givers(name="Demo Giver", email="demo@fake.com", picture="http://www.hookedgamers.com/images/1219/shaun_the_sheep_off_his_head/header_shaun_the_sheep_off_his_head.jpg")

otherGiver = Givers(name="Other Giver", email="other@fake.com", picture="http://img05.deviantart.net/0ea8/i/2005/123/a/1/wakko_from_animaniacs_by_kazooey.png")

session.add(demoGiver)
session.add(otherGiver)
session.commit()


# Recipients for Demo Giver
recipientOne = Recipients(name="Yakko Warner", bday="Apr 2", sizes="medium", givers=demoGiver)
recipientTwo = Recipients(name="Wakko Warner", bday="July 31", sizes="small", givers=demoGiver)
recipientThree = Recipients(name="Dot Warner", bday="Oct 22", sizes="xsmall", givers=demoGiver)

session.add(recipientOne)
session.add(recipientTwo)
session.add(recipientThree)
session.commit()


# Gifts for Demo Giver, recipientOne
today = datetime.date.today()
giftOne = Gifts(name="Rocket Pogo Stick", desc="Foam covered metal frame, Non slip foot pads", link="http://www.amazon.com/Flybar-Chrome-Rocket-Pogo-Stick/dp/B00XAJ22UO", image="http://c.shld.net/rpx/i/s/pi/mp/27954/prod_3316190121?src=http%3A%2F%2Fcp75.com%2FABS%2FImages%2F31ckOoF4GGL._SS400_.jpg&d=5569f97370c33c13b33e9cceddf160f7a33903a4&hei=245&wid=245&op_sharpen=1&qlt=85", status="idea", date_added=today, givers=demoGiver, recipients=recipientOne)
giftTwo = Gifts(name="100-Piece Wooden Block Set", desc="Variety of shapes: rectangular prisms, cubes, cylinders, half circles, arches, rectangular planks and triangles.", link="http://www.amazon.com/Melissa-Doug-100-Piece-Wood-Blocks/dp/B000068CKY", image="http://www.brightbeans.co.za/images/detailed/1/Melissa&Doug_100_Piece_Wood_Block_Set_2137510294751f667e397fb2.png", status="purchased", date_added=today, givers=demoGiver, recipients=recipientOne)
giftThree = Gifts(name="Blue Acoustic Guitar", desc="38 inch body, and blue!", link="http://www.amazon.com/Acoustic-Starter-Beginner-DirectlyCheap-Translucent/dp/B006CYVD5E", image="http://ecx.images-amazon.com/images/I/41lCP%2BMck3L.jpg", status="idea", date_added=today, givers=demoGiver, recipients=recipientOne)

session.add(giftOne)
session.add(giftTwo)
session.add(giftThree)
session.commit()


# Gifts for Demo Giver, recipientTwo
today = datetime.date.today()
giftOne = Gifts(name="Adventure Science: Chemistry Blast", desc="Young Scientists create sticky ice, remove gas from soda, and make flower change colors. Young Scientists use test tubes, filter paper, and funnel to separate mixture of materials and making an explosion that will excite any budding scientist", link="http://www.amazon.com/Adventure-Science-series-Chemistry-Blast/dp/B000E9TBNO", image="http://ecx.images-amazon.com/images/I/81IVMXCDl-S._SX425_.jpg", status="idea", date_added=today, givers=demoGiver, recipients=recipientTwo)
giftTwo = Gifts(name="Classic Mini Djembe Drum", desc="Desktop Djembe, perfect drum for small children, classrooms, or lunchtime jams; 4in Playing Surface, 8in Height", link="http://www.amazon.com/Africa-Heartwood-Project-SD4X8-Classic/dp/B006CQ8PGC", image="http://ecx.images-amazon.com/images/I/41L2Qz3u23L._SY355_.jpg", status="purchased", date_added=today, givers=demoGiver, recipients=recipientTwo)
giftThree = Gifts(name="KPC Pro Skateboard Complete", desc="Canadian Maple Construction; 7.75-Inch Deck", link="http://www.amazon.com/KPC-Skateboard-Complete-Black-Checker/dp/B004UOL6BO", image="http://ecx.images-amazon.com/images/I/41curokU5dL._SY355_.jpg", status="idea", date_added=today, givers=demoGiver, recipients=recipientTwo)

session.add(giftOne)
session.add(giftTwo)
session.add(giftThree)
session.commit()


# Gifts for Demo Giver, recipientThree
today = datetime.date.today()
giftOne = Gifts(name="Mini Bass Guitar", desc="Pink; Only 31.5inch overall length (smallest bass guitar on the market)", link="http://www.amazon.com/MB1-Quality-small-guitar-travel/dp/B00Q9TBWTE", image="http://ecx.images-amazon.com/images/I/41DK-PhwBGL.jpg", status="idea", date_added=today, givers=demoGiver, recipients=recipientThree)
giftTwo = Gifts(name="Razor A2 Kick Scooter", desc="Made of sturdy aircraft-grade aluminum with red highlights", link="http://www.amazon.com/Razor-A2-Kick-Scooter-Red/dp/B00005MOYK", image="http://www.toysrus.com/graphics/product_images/pTRU1-3029018dt.jpg", status="idea", date_added=today, givers=demoGiver, recipients=recipientThree)

session.add(giftOne)
session.add(giftTwo)
session.commit()


# Recipients for Other Giver
recipientOne = Recipients(name="Bart Simpson", bday="Mar 2", sizes="medium", givers=otherGiver)
recipientTwo = Recipients(name="Lisa Simpson", bday="June 31", sizes="small", givers=otherGiver)
recipientThree = Recipients(name="Maggie Simpson", bday="Sept 22", sizes="6 mo", givers=otherGiver)

session.add(recipientOne)
session.add(recipientTwo)
session.add(recipientThree)
session.commit()


# Gifts for Other Giver, recipientOne
today = datetime.date.today()
giftOne = Gifts(name="WubbaNub Brown Monkey", desc="Pacifier attached permanently to stuffed animal", link="http://www.amazon.com/WubbaNub-WN22330-Brown-Monkey/dp/B0028IDXDS", image="http://ecx.images-amazon.com/images/I/712ym48jIHL._SX522_.jpg", status="purchased", date_added=today, givers=otherGiver, recipients=recipientThree)
giftTwo = Gifts(name="Transforming High Chair", desc="Chair adjusts as your child ages.", link="http://www.amazon.com/Abiie-Perfect-Highchair-Solution-Toddlers/dp/B00BSD7PMY/", image="http://ecx.images-amazon.com/images/I/81hq-8nUxQL._SL1500_.jpg", status="idea", date_added=today, givers=otherGiver, recipients=recipientThree)

session.add(giftOne)
session.add(giftTwo)
session.commit()


# Gifts for Other Giver, recipientTwo
today = datetime.date.today()
giftOne = Gifts(name="Junior Toy Saxophone", desc="The Bontempi Junior Saxophone offers 4 colored keys/notes", link="http://www.amazon.com/Junior-Toy-Saxophone-by-Bontempi", image="http://ecx.images-amazon.com/images/I/51fxtTaDF9L._SY355_.jpg", status="purchased", date_added=today, givers=otherGiver, recipients=recipientTwo)
giftTwo = Gifts(name="Creativity for Kids Butterfly Necklaces", desc="Create 6 beautiful butterfly necklaces", link="http://www.amazon.com/Creativity-for-Kids-Butterfly-Necklaces/dp/B00BUSZ1I2", image="http://cdn3.bigcommerce.com/s-ovsa8in/products/10623/images/13340/TNW-560274-2__06359.1440331991.650.650.jpg?c=2", status="idea", date_added=today, givers=otherGiver, recipients=recipientTwo)

session.add(giftOne)
session.add(giftTwo)
session.commit()
