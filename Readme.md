# Project: Gifter - by jennifer lyden

## Synopsis
Maintains lists of Givers; Recipients associated with a particular Giver; and Gifts, associated with a particular Giver and Recipient, classified as idea, purchased, or given, with images and links.

## Required Libraries and Dependencies
* You will need Python v2 or higher, SQLAlchemy, Flask, oauth2client, xml.etree.ElementTree, and SeaSurf to run this project.
* You will also need the following Python modules: httplib2, requests, json, and datetime.
* If you don't already have python on your machine, you could run the system on a Vagrant Virtual Machine. Udacity's instructions for VM installation are here: https://www.udacity.com/wiki/ud197/install-vagrant
    * If you use the Vagrant VM, you will need to install SeaSurf - `pip install flask-seasurf`

## Installation

### To Install
Download the zip file and extract the "gifter" folder inside.

### To Setup the Database
Start up your VM and navigate to your new "gifter" folder.
From the command line, run `python gifter_db_setup.py` to create a database containing three tables: Givers, Recipients and Gifts.
Then run `python demo_setup.py` to add Demo Giver with recipients and gifts.

### To Run
From the command line, run `python project.py` Now Gifter is up and running. You can visit it locally at by opening http://localhost:5000 in a web browser.

### To Test App
* When you get to the Gifter welcome page, you can "Register" to create a new Gifter account associated with your Google+ or Facebook account. 
    * From there, you can create, edit, and delete Recipients and Gifts. Also, if you click "All Gifts" in the navigation bar, you can see all the gifts entered into the database by any user.
* Alternately, you could "Explore the Demo." This option logs you in as Demo Giver, which already has Recipients and Gifts associated with it. 
    * You can create, edit or delete those demo recipients and gifts as desired.
    * Furthermore, 




## Extra Credit Description
