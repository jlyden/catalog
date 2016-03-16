# Project: Gifter (P5) - by jennifer lyden

## Synopsis
* Maintains lists of Givers; Recipients associated with a particular Giver; and Gifts, associated with a particular Giver and Recipient, classified as idea, purchased, or given, with images and links.

### Readme-P5 vs Readme-P3
* These instructions explain how to set up a server on Amazon AWS and then deploy the app on that server. If you don't need to set-up a server, see Readme-P3 for streamlined instructions.

### Accessing the Deployed App
- IP Address: 52.37.189.129
- SSH port: 2200
- URL: http://ec2-52-37-189-129.us-west-2.compute.amazonaws.com

### Software Installed & Configuration Changes
#### Users:
1. Login as *root*, add two users, *grader* and *jenny*, and set passwords for each.
2. Add files in `/etc/sudoers.d` for *grader* and *jenny* to give them `sudo` power with password; adjust file permissions
3. Set up Key-Based Authentication
   * Edit `/etc/ssh/sshd_config` to allow Password-Authentication (temporarily!)
   * Generate new key for *jenny* on local machine; use *jenny* + password to login and copy public key to newly-created `~/.ssh/authorized_keys`
   * Copy public key from *root*; use *grader* + password  to login and copy and copy public key to newly-created `~/.ssh/authorized_keys`
4. Logout *root*. Complete all future actions with *jenny* user.

#### Update/Upgrade, Time and Firewall Configuration
1. Update, upgrade, autoremove & restart server
2. Run `sudo dpkg-reconfigure tzdata`; select "None of the Above", "UTC" from menus
3. Install **ntp**; in `/etc/ntp.conf`, change "server 0.ubuntu.pool.ntp.org" to "server 0.us.pool.ntp.org" (for all four servers)
4. Resolve error "sudo: unable to resolve host [name]" by adding [name] to end of first line of `/etc/hosts`
5. Edit `/etc/ssh/sshd_config`; after each change `sudo reload ssh` and test login to confirm continued access
   * Set "Password-Authentication" and "PermitRootLogin" to "no"
   * Under "# What port, IPs and protocols we listen for", change to `Port 2200`
6. Configure and enable UFW
   * deny incoming, allow outgoing, allow 2200, deny 22, allow http, allow ntp
   * After `sudo ufw enable`, double check rules: `sudo ufw status verbose`

#### Apache and Postgres Installation and Setup
1. Install **Apache** with **mod_wsgi**, plus **python-dev** and **python-setuptools**
   * Edit `/etc/apache2/apache2.conf` to change "Timeout 30"
2. Install **Postgres** & **psycopg2**
   * Edit `/etc/postgresql/9.3/main/pg_hba.conf` to confirm no remote connections
   * Login to Postgres user account: `sudo -i -u postgres`
   * Create new Postgres role: `createuser --interactive -P`
        * name and password = catalog
   * Create database: `createdb catalog`
   * Connect to database: `psql -d catalog`
   * Set permissions: 
        * `REVOKE ALL ON SCHEMA public FROM public;`
        * `GRANT ALL ON SCHEMA public TO catalog;`
   * Exit database and logout of postgres

#### Flask Setup and App Installation
1. Create and move to FlaskApp Directory: `sudo mkdir /var/www/Gifter`, `cd /var/www/Gifter`
2. Install **git** and clone repo from github: `sudo git clone https://github.com/jlyden/catalog.git`
   * App arrives in "catalog" folder, so renaming needed
        * `sudo mv catalog Gifter`
        * `sudo mv Gifter/project.py Gifter/__init__.py`
3. Protect .git dir from visibility
   * Create `/var/www/Gifter/.htaccess`
   * Enter `RedirectMatch 404 /\.git` on first line and save/exit
4. Configure & enable new Apache VirtualHost
   * Create `/etc/apache2/sites-available/Gifter.conf` (text from [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps))
        * Set `ServerName 52.37.189.129` and `ServerAlias ec2-52-37-189-129.us-west-2.compute.amazonaws.com`
   * Activate VirtualHost: `sudo a2ensite Gifter`
   * Create `/var/www/Gifter/gifter.wsgi` (text from [DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps))
        * pull secret_key from `__init__.py` (line 833)
   * Restart Apache: `sudo service apache2 restart`
5. Set up Virtual Environment and install Flask and other dependencies
   * Install **python-pip**, **virtualenv**
   * Setup and activate virtualenv in `/var/www/Gifter/Gifter`
        * `sudo virtualenv env`; `source env/bin/activate`
   * Install inside virtualenv: **Flask**, **flask-seasurf**, **SQLAlchemy**, **oauth2client**
        * I read that `sudo pip` inside virtualenv is bad form, but when I omitted `sudo` exceptions were thrown
   * Deactivate virtualenv
6. Edit to get app up and running with postgres
   * In `__init__.py`, `gifter_db_setup.py`, `demo_setup.py` ... 
        * add `import psycopg2`
        * change ConnectString to `postgresql+psycopg2://catalog:catalog@localhost/catalog`
   * Setup Database & Demo Data
        * `python gifter_db_setup.py`; `python demo_setup.py`
7. Update *catalog* user permissions on postgres database tables
   * Login to postgresql - `sudo -i -u postgres`
   * Connect to catalog & see tables - `psql -d catalog` & `\d`
   * `GRANT INSERT, SELECT, UPDATE, DELETE ON gifts, givers, recipients TO catalog;` 
   * Verify permissions - `\z` and exit - `\q`; `logout`
8. Oauth Updates - Google
   * Google Developers Console -> Enable and manage APIs -> Credentials -> Gifter App under "OAuth 2.0 client IDs" -> Add public address (http://ec2-52-37-189-129.us-west-2.compute.amazonaws.com) under "Authorized JavaScript origins" and "Authorized redirect URIs" (with /oauth2callback)
   * Download JSON and paste into `/var/www/Gifter/Gifter/client_secrets.json`
   * Back to Credentials -> Gifter key under "API keys" -> Add public address (http://ec2-52-37-189-129.us-west-2.compute.amazonaws.com) under "Accept requests from these ..."
9. Oauth Updates - Facebook
   *  Facebook Developers Console -> Settings -> Change Site URL [Save Changes] -> Advanced -> Add public address to "Valid OAuth redirect URIs" [Save Changes] -> Basic
   * Copy App ID & App Secret and paste into `/var/www/Gifter/Gifter/fb_client_secrets.json`
10. Reload Apache: `sudo service apache2 reload` and visit website to confirm it's working!
    * If not immediately working, disable Apache's default VirtualHost and restart Apache: `sudo a2dissite default`
    * If needed, view Apache logs to troubleshoot: `sudo tail /var/log/apache2/error.log`

#### Additional Functionality
1. Install **fail2ban** to Monitor for unsuccessful login attempts
    * Setup and edit local "jail": `sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local`
        * `bantime 1800` [30 min]
        * `action = %(action_)s`
        * [under ssh] - `port = 2200`
        * [under apache] - `enabled = true`
        * [under apache-overflows] - `enabled = true`
        * I was going to setup mail notifications, but I didn't know how to solve the domain name issue
2. Install **unattended upgrades** to automatically manage package updates
    * Edit `/etc/apt/apt.conf.d/50unattended-upgrades`
        * Uncomment `Ubuntu precise-updates` under `Unattended-Upgrade::Allowed-Origins`
        * I would enter e-mail address but see earlier mail-setup-issues (MailOnlyOnError "true")
    * Edit `/etc/apt/apt.conf.d/10periodic`
        * Follow [Ubuntu schedule](https://help.ubuntu.com/12.04/serverguide/automatic-updates.html) - daily update of package lists, download & upgrade of packages; weekly autoclean
3. Install **glances** to monitor server usage

## Resources Consulted
* Configure time - local timezone to UTC & NTP server: https://help.ubuntu.com/community/UbuntuTime#Using_the_Command_Line_.28terminal.29
* Change SSH Port: https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-12-04 - see "Step Five"
* Configure UFW: https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-14-04
* Udacity's LAMP setup guide:  http://blog.udacity.com/2015/03/step-by-step-guide-install-lamp-linux-apache-mysql-python-ubuntu.html
* Configure Apache w/Flask:
    - https://www.digitalocean.com/community/tutorials/how-to-configure-the-apache-web-server-on-an-ubuntu-or-debian-vps
    - https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
    - http://serverfault.com/questions/128069/how-do-i-prevent-apache-from-serving-the-git-directory
* Apache Log files:  https://www.a2hosting.com/kb/developer-corner/apache-web-server/viewing-apache-log-files
* Understanding Virtual Environments: https://www.dabapps.com/blog/introduction-to-pip-and-virtualenv-python/
* Postgres Setup:
    - https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04
    - https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps
    - Roles & Permissions: http://www.davidpashley.com/articles/postgresql-user-administration/
* Pointing to files via relative path:  https://discussions.udacity.com/t/target-wsgi-script-cannot-be-loaded-no-such-file/44819
* Fail2ban: Monitor for unsuccessful login attempts
    - https://www.digitalocean.com/community/tutorials/how-to-protect-an-apache-server-with-fail2ban-on-ubuntu-14-04
    - https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-postfix-as-a-send-only-smtp-server-on-ubuntu-14-04
* Automatic Updates (Ubuntu recommendation): https://help.ubuntu.com/12.04/serverguide/automatic-updates.html
* Glances (monitor server resources): http://glances.readthedocs.org/en/latest/glances-doc.html

### To Test App
* When you get to the Gifter welcome page, you can "Register" to create a new Gifter account associated with your Google+ or Facebook account.
    * From there, you can create, edit, and delete Recipients and Gifts.
* Alternately, you could "Explore the Demo." This option logs you in as Demo Giver, which already has Recipients and Gifts associated with it.
    * You can create, edit or delete those demo recipients and gifts as desired.
* Test authorization for editing and deleting gifts as Demo Giver or from your own account:
    * Click "All Gifts" in the navigation bar. Now you can see all the gifts entered into the database by any user.
    * Click any gift to see it's details. If you click a gift like "WubbaNub Brown Monkey" which is NOT associated with Demo Giver, you will not be permitted to Change Status, Edit or Delete. However, you could still "Give to Another," which makes a new copy of the gift associated with the current user (i.e. Demo Giver).

## Additional Info
I know there are more features here than required for P3, but when I started working on this project, I wanted to make something that would be actually useful beyond the Nanodegree assignment. I hope you didn't mind wading through the extra features. Thanks!
