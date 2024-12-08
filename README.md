# odoo-challenge-backend
Odoo Challenge Backend

## Introduction
In this tutorial you will install Odoo and a PostgreSQL database using Docker Compose. If you are using cloud server, you can also install Nginx to act as a reverse proxy for your Odoo site. Finally, you will enable secure HTTPS connections by using Certbot to download and configure a TLS certificate from the Let’s Encrypt Certificate Authority.

## Prerequisite
Ubuntu 18 or above

### SSH into Cloud Server
ssh -i "server-key.pem" username@SERVER_IP


### Step 1 — Installing Docker Compose
To install the docker-compose command line tool, refresh your package list, then install the package using apt:

sudo apt update
sudo apt install docker-compose

You can confirm that the package is installed by running the following command:

docker-compose –-version

You should receive output like the following:

Output
docker-compose version 1.29.2, build unknown

Once you have confirmed that Docker Compose is installed on your server, you will configure and launch Odoo and PostgreSQL using Docker Compose in the next step of this tutorial.

### Step 2 — Running Odoo and PostgreSQL with Docker Compose
To get started creating your Odoo and PostgreSQL containers, create a directory called odoo in your home directory to store the files that you will create in this tutorial. You’ll use this directory to store all the files that you need to run Odoo.

Run the following commands to create the directory and then cd into it:

mkdir ~/odoo
cd ~/odoo

Add custom-addons folder:

mkdir custom-addons
cd custom-addons
git init
git remote add origin https://github.com/ariful-beleaf/odoo-challenge-backend.git
git fetch origin main
git checkout main

Go back to previous folder:
cd ..


Create a dockerfile for installing python dependency 
nano dockerfile

`
FROM odoo:17.0

USER root

# Install Python packages
RUN pip3 install PyJWT

USER odoo
`

Now open a new blank YAML file called docker-compose.yml using nano or your preferred editor:
nano docker-compose.yml


version: '3'
services:
  odoo:
    build: .  # This tells Docker to use your Dockerfile
    image: odoo:17.0
    env_file: .env
    depends_on:
      - postgres
    ports:
      - "0.0.0.0:8069:8069"
    volumes:
      - data:/var/lib/odoo
      - ./custom-addons:/mnt/extra-addons  # Add this line
    environment:
      - ADDONS_PATH=/mnt/extra-addons  # Add this line
  postgres:
    image: postgres:14
    env_file: .env
    volumes:
      - db:/var/lib/postgresql/data/pgdata

volumes:
  data:


Build for installing python dependency:

docker-compose build

You can also verify the installation by accessing the container and checking:
docker-compose exec odoo pip3 list | grep jwt

This should show PyJWT in the list of installed packages.


You will use this file with the docker-compose command to start your Odoo and PostgreSQL containers and link them together. Add the following lines to the file:


Open a new .env file with nano:

nano .env
Add the following lines into the file, substituting in a POSTGRES_USER and POSTGRES_PASSWORD of your choice in place of the highlighted values:

.env
# postgresql environment variables
POSTGRES_DB=postgres
POSTGRES_PASSWORD=r620ILVYRyTc5QBMGYCGX9dPqD6wOiunk14Cwv/k
POSTGRES_USER=odoo7
PGDATA=/var/lib/postgresql/data/pgdata

# odoo environment variables
HOST=postgres
USER=odoo17
PASSWORD=1V5TLPDFKM7tIIdiBn8c10uoxyJ5yEKKwlH0k4+H

To generate a password for Odoo and PostgreSQL, use the openssl command, which should be available on most Linux systems. Run the following command on your server to generate a random set of bytes and print a base64 encoded version that you can use as a password:

openssl rand -base64 30
Paste the resulting string into your .env file in place of the a_strong_password_for_user placeholder passwords.

When you’re done editing your .env file, save and exit your text editor.

You’re now ready to start the odoo and postgres containers with the docker-compose command:


docker-compose up -d
The up sub-command tells docker-compose to start the containers and the associated volumes and networks that are defined in the docker-compose.yml file. The -d flag (which stands for “daemonize”) tells docker-compose to run the containers in the background so the command doesn’t take over your terminal. docker-compose will print some brief output as it downloads the required Docker images and then starts the containers:

Output
Creating network "odoo_default" with the default driver
Creating volume "odoo_odoo_data" with default driver
Creating volume "odoo_postgres_data" with default driver
Pulling odoo (odoo:14.0)...
15.0: Pulling from library/odoo
. . .


If you would like to stop your Odoo and PostgreSQL containers at any time, run the following command in your ~/odoo directory:

docker-compose stop
The containers will be stopped. The configuration and data in their volumes will be preserved so that you can start the containers again with the docker-compose up -d command.

When that’s done, Odoo should be running. You can test that a webserver is running at 127.0.0.1:8069 by fetching the homepage using the curl command:

curl --head http://localhost:8069
This will print out only the HTTP headers from the response:

Output
HTTP/1.0 303 SEE OTHER
Content-Type: text/html; charset=utf-8
Content-Length: 215
Location: http://localhost:8069/web
Set-Cookie: session_id=142fa5c02742d0f5f16c73bc14ec8144b8230f8a; Expires=Mon, 06-Jun-2022 20:45:34 GMT; Max-Age=7776000; HttpOnly; Path=/
Server: Werkzeug/0.14.1 Python/3.7.3
Date: Tue, 08 Mar 2022 20:45:34 GMT
The 303 SEE OTHER response means the Odoo server is up and running, but that you should visit another page to complete the installation. The highlighted http://localhost:8069/web Location header indicates where to visit the Odoo installer page in your browser.

### Open Odoo Instance
Go to browser and use: http://SERVER_IP:8069
A Database ceation form will come.

The information that you fill in on this page will tell the Odoo application how to create its PostgreSQL database and details about the default administrative user.

Fill out the following fields:

Database Name: odoo
Email: your email address
Password: a strong and unique password for your administrator login
Demo data: ensure that this option is checked if this is the first time that you are installing odoo
The defaults are fine for the remaining fields. Be sure to record the email and password values that you choose since you will use them to login to Odoo in the future.

Now click the Create database button at the bottom left of the page. It may take a minute or two for Odoo to create its database tables. When the process is complete you will be redirected to the Odoo Apps administrative page.

Once Database is ready, login with your given username and password.
Now, for installing the custom modules:
Go to Apps
Click on Update Apps List
A pop up comes with "Module Update"
Now click on "Update"
Go to Search Filter and remove all filter
Search by "auth_custom" and "event_custom"
Install both modules



Next we’ll set up Nginx to proxy public traffic to the Odoo container.

### Step 3 — Installing and Configuring Nginx
If you are using cloud server, you can also configure nginx based on your requirements.

Putting a web server such as Nginx in front of your Odoo server can improve performance by offloading caching, compression, and static file serving to a more efficient process. We’re going to install Nginx and configure it to reverse proxy requests to Odoo, meaning it will take care of handing requests from your users to Odoo and back again. Using a non-containerized Nginx process will also make it easier to add Let’s Encrypt TLS certificates in the next step.

First, refresh your package list, then install Nginx using apt:

sudo apt update
sudo apt install nginx

sudo ufw allow "Nginx Full"

Output
Rule added
Rule added (v6)

Next, open up a new Nginx configuration file in the /etc/nginx/sites-available directory. We’ll call ours odoo.conf but you could use a different name:
sudo nano /etc/nginx/sites-available/odoo.conf

Paste the following into the new configuration file, being sure to replace your_domain_here with the domain that you’ve configured to point to your Odoo server. This should be something like odoo.example.com, for instance:

/etc/nginx/sites-available/odoo.conf
server {
    listen       80;
    listen       [::]:80;
    server_name  your_domain_here;

    access_log  /var/log/nginx/odoo.access.log;
    error_log   /var/log/nginx/odoo.error.log;

    location / {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-Host $host;
      proxy_set_header X-Forwarded-Proto https;
      proxy_pass http://localhost:8069;
  }
}

This configuration is HTTP-only for now, as we’ll let Certbot take care of configuring TLS in the next step. The rest of the configuration file sets up logging locations and then passes all traffic, as well as some important proxy headers, along to http://localhost:8069, the Odoo container that we started up in the previous step.

Save and close the file, then enable the configuration by linking it into /etc/nginx/sites-enabled/:

sudo ln -s /etc/nginx/sites-available/odoo.conf /etc/nginx/sites-enabled/

sudo nginx -t
Output
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
And finally, reload the nginx service with the new configuration:

sudo systemctl reload nginx.service

Your Odoo site should now be available on plain HTTP. Load http://your_domain_here (you may have to click through a security warning) and it will look like this:

Now that you have your site up and running over HTTP, it’s time to secure the connection with Certbot and Let’s Encrypt certificates. You should do this before going through Odoo’s web-based setup procedure.

### Step 4 — Installing Certbot and Setting Up TLS Certificates
Thanks to Certbot and the Let’s Encrypt free certificate authority, adding TLS encryption to your Odoo app will take only two commands.

First, install Certbot and its Nginx plugin:

sudo apt install certbot python3-certbot-nginx
Next, run certbot in --nginx mode, and specify the same domain that you used in the Nginx server_name configuration directive:

sudo certbot --nginx -d your_domain_here
You’ll be prompted to agree to the Let’s Encrypt terms of service, and to enter an email address.

Afterwards, you’ll be asked if you want to redirect all HTTP traffic to HTTPS. It’s up to you, but this is generally recommended and safe to do.

After that, Let’s Encrypt will confirm your request and Certbot will download your certificate:

Output
Congratulations! You have successfully enabled https://odoo.example.com

You should test your configuration at:
https://www.ssllabs.com/ssltest/analyze.html?d=odoo.example.com
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

IMPORTANT NOTES:
 - Congratulations! Your certificate and chain have been saved at:
   /etc/letsencrypt/live/odoo.example.com/fullchain.pem
   Your key file has been saved at:
   /etc/letsencrypt/live/odoo.example.com/privkey.pem
   Your cert will expire on 2022-05-09. To obtain a new or tweaked
   version of this certificate in the future, simply run certbot again
   with the "certonly" option. To non-interactively renew *all* of
   your certificates, run "certbot renew"
 - Your account credentials have been saved in your Certbot
   configuration directory at /etc/letsencrypt. You should make a
   secure backup of this folder now. This configuration directory will
   also contain certificates and private keys obtained by Certbot so
   making regular backups of this folder is ideal.
 - If you like Certbot, please consider supporting our work by:

   Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
   Donating to EFF:                    https://eff.org/donate-le
Certbot will automatically reload Nginx with the new configuration and certificates. Reload your site in your browser and it should switch you over to HTTPS automatically if you chose the redirect option.

Your site is now secure and it’s safe to continue with the web-based setup steps.

### Step 5 — Setting Up Odoo
Back in your web browser, reload the page. You should now have Odoo’s database configuration page open via a secure https:// connection. Now you can enter usernames and passwords safely to complete the installation process.

The information that you fill in on this page will tell the Odoo application how to create its PostgreSQL database and details about the default administrative user.

Fill out the following fields:

Database Name: odoo
Email: your email address
Password: a strong and unique password for your administrator login
Demo data: ensure that this option is checked if this is the first time that you are installing odoo
The defaults are fine for the remaining fields. Be sure to record the email and password values that you choose since you will use them to login to Odoo in the future.

Now click the Create database button at the bottom left of the page. It may take a minute or two for Odoo to create its database tables. When the process is complete you will be redirected to the Odoo Apps administrative page.


From here you can choose which Odoo modules you would like to install and use for your ERP needs. If you would like to test an app, click the Install button on the Sales tile. Odoo will install the module and then redirect you to your personal Discuss app page.

Click the segmented square icon at the top left of your screen and then select the Sales link in the list of dropdown options.

Screenshot of Odoo's Sales app dashboard with customization options

You will be on a page that will guide you through customizing data, quotes, orders, and a list of example sales that you can experiment with.

### Conclusion
In this tutorial, you launched the Odoo ERP app and a PostgreSQL database using Docker Compose, then set up an Nginx reverse proxy and secured it using Let’s Encrypt TLS certificates.

You’re now ready to start building your ERP website using the supplied modules. 