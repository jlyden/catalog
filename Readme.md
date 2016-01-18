# Project: Gifter - by jennifer lyden

## Synopsis
Maintains lists of Givers; Recipients associated with a particular Giver; and Gifts, associated with a particular Giver and Recipient, classified as idea, purchased, or given, with images and links.

## Required Libraries and Dependencies
* You will need Python v2 or higher, SQLAlchemy, Flask, oauth2client, xml.etree.ElementTree, and SeaSurf to run this project.
* You will also need the following Python modules: httplib2, requests, json, and datetime.
* If you don't already have Python on your machine, you could run the system on a Vagrant Virtual Machine. Udacity's instructions for VM installation are here: https://www.udacity.com/wiki/ud197/install-vagrant
    * If you use the Vagrant VM, you will need to install SeaSurf - `pip install flask-seasurf`

## Installation

### To Install
Download the zip file and extract the "gifter" folder inside.

### To Setup the Database
* Start up your VM and navigate to your new "gifter" folder.
* From the command line, run `python gifter_db_setup.py` to create a database containing three tables: Givers, Recipients and Gifts.
* Then run `python demo_setup.py` to add Demo Giver with recipients and gifts.

### NOTE: Client Secrets
* The included "client_secrets.json" and "fb_client_secrets.json" files contain multiple [ENTER YOUR OWN] fields. Replace them before running. 


### To Run
From the command line, run `python project.py` Now Gifter is up and running. You can visit it locally at by opening http://localhost:5000 in a web browser.

### To Test App
* When you get to the Gifter welcome page, you can "Register" to create a new Gifter account associated with your Google+ or Facebook account.
    * From there, you can create, edit, and delete Recipients and Gifts.
* Alternately, you could "Explore the Demo." This option logs you in as Demo Giver, which already has Recipients and Gifts associated with it.
    * You can create, edit or delete those demo recipients and gifts as desired.
* Test authorization for editing and deleting gifts as Demo Giver or from your own account:
    * Click "All Gifts" in the navigation bar. Now you can see all the gifts entered into the database by any user.
    * Click any gift to see it's details. If you click a gift like "WubbaNub Brown Monkey" which is NOT associated with Demo Giver, you will not be permitted to Change Status, Edit or Delete. However, you could still "Give to Another," which makes a new copy of the gift associated with the current user (i.e. Demo Giver).

## Extra Credit Description
* I added an additional API Endpoint - XML.
* I added support for image links in the creation, reading, and updating of catalog items. I also coded for a default image to be displayed if a person does not provide a link.
* I added SeaSurf to provide protection from CSRF attacks.
* I ran python code through a pep8 checker, and css code through a validator.
    * I had issues with my html code, since it had {{}} - any recommendations?

## Additional Info
I know there are more features here than required, but when I started working on this project, I wanted to make something that would be actually useful beyond Udacity FullStack Nanodegree P3. I hope you didn't mind wading through the extra features. Thanks!
