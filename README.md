In order to create a Facebook Messenger Bot you need to create a Facebook App.

Facebook App allows you to retrieve and post data on Facebook programatically via Facebook API.
Facebook API provides the interface and methods to interact with the Facebook App.

Setup FB page and app:
+ Go to http://developers.facebook.com
+ Create a Facebook page (if you do not already have it)
+ Create a Facebook app for Facebook Messanger (provide a name and a contact email address)
+ Generate a Token for the Facebook Page with which you want to integrate (this is the PAGE_ACCESS_TOKEN)

Setup the FB webhook:
+ give it the Callback URL (the one you will get when you create the heroku app)
+ enter the Verify Token (this is the VERIFY_TOKEN)
+ check all the Subscription Fields -> verify and save
+ subscribe webhook to the page events on your FB Page

Setup your project:
+ install git, python3, python3-venv
+ git clone [https://github.com/anuschka/fb-messenger-bot-python.git]
+ cd into fb-messenger-bot-python
+ create a virtual environment inside the *fb-messenger-bot-python* directory *python3 -m venv venv* 
+ activate the virtual environment *source venv/bin/activate*
+ install python dependencies *pip install -r requirements.txt*
+ setup environment variables: 
    + export FLASK_APP=app.py
    + export PAGE_ACCESS_TOKEN=the-token-you-setup-on-the-facebook-messenger-app
    + export VERIFY_TOKEN=the-token-you-setup-on-on-the-facebook-webhook

Test the app locally:
+ flask run
+ http://127.0.0.1:5000/ should give you *Hello world*

Setup heroku and git:
+ install heroku-cli
+ git add .
+ git commit -m "My initial commit"

Deploy to heroku:
+ create a heroku app *heroku create* 
    + this is the URL you will use for the webhook callback
+ heroku git:remote -a name-of-the-heroku-app-from-the-previous-step
+ git push heroku master

Test the FB chatbot:
+ send a message from your FB account to the FB Page and it should echo it back
+ you can see the message in the heroku app log
+ tada

