import os
import sys
import json

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])   
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":   # make sure this is a page subscription

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):     # someone sent us a message
                    received_message(messaging_event)

                elif messaging_event.get("delivery"):  # delivery confirmation
                    pass
                    # received_delivery_confirmation(messaging_event)

                elif messaging_event.get("optin"):     # optin confirmation
                    pass
                    # received_authentication(messaging_event)

                elif messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    received_postback(messaging_event)

                else:    # uknown messaging_event
                    log("Webhook received unknown messaging_event: " + messaging_event)

    return "ok", 200


def received_message(event):

    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
    
    # could receive text or attachment but not both
    if "text" in event["message"]:
        message_text = event["message"]["text"]

        # parse message_text and give appropriate response   
        if message_text == 'image':
            send_image_message(sender_id)

        elif message_text == 'file':
            send_file_message(sender_id)

        elif message_text == 'audio':
            send_audio_message(sender_id)

        elif message_text == 'video':
            send_video_message(sender_id)

        elif message_text == 'button':
            send_button_message(sender_id)

        elif message_text == 'generic':
            send_generic_message(sender_id)

        elif message_text == 'share':
            send_share_message(sender_id)

        else: # default case
            send_text_message(sender_id, "Echo: " + message_text)

    elif "attachments" in event["message"]:
        message_attachments = event["message"]["attachments"]   
        send_text_message(sender_id, "Message with attachment received")


# Message event functions
def send_text_message(recipient_id, message_text):

    # encode('utf-8') included to log emojis to heroku logs
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text.encode('utf-8')))

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })

    call_send_api(message_data)


def send_generic_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [{
                        "title": "rift",
                        "subtitle": "Next-generation virtual reality",
                        "item_url": "https://www.oculus.com/en-us/rift/",               
                        "image_url": "http://messengerdemo.parseapp.com/img/rift.png",
                        "buttons": [{
                            "type": "web_url",
                            "url": "https://www.oculus.com/en-us/rift/",
                            "title": "Open Web URL"
                        }, {
                            "type": "postback",
                            "title": "Call Postback",
                            "payload": "Payload for first bubble",
                        }],
                    }, {
                        "title": "touch",
                        "subtitle": "Your Hands, Now in VR",
                        "item_url": "https://www.oculus.com/en-us/touch/",               
                        "image_url": "http://messengerdemo.parseapp.com/img/touch.png",
                        "buttons": [{
                            "type": "web_url",
                            "url": "https://www.oculus.com/en-us/touch/",
                            "title": "Open Web URL"
                        }, {
                            "type": "postback",
                            "title": "Call Postback",
                            "payload": "Payload for second bubble",
                        }]
                    }]
                }
            }
        }
    })

    log("sending template with choices to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)
    

def send_image_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"image",
                "payload":{
                    "url":"http://i.imgur.com/76rJlO9.jpg"
                }
            }
        }
    })

    log("sending image to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def send_file_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"file",
                "payload":{
                    "url":"http://ee.usc.edu/~redekopp/ee355/EE355_Syllabus.pdf"
                }
            }
        }
    })

    log("sending file to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def send_audio_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"audio",
                "payload":{
                    "url":"http://www.stephaniequinn.com/Music/Allegro%20from%20Duet%20in%20C%20Major.mp3"
                }
            }
        }
    })

    log("sending audio to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def send_video_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"video",
                "payload":{
                    "url":"http://techslides.com/demos/sample-videos/small.mp4"
                }
            }
        }
    })

    log("sending video to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def send_button_message(recipient_id):

    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"template",
                "payload":{
                    "template_type":"button",
                    "text":"What do you want to do next?",
                    "buttons":[
                    {
                        "type":"web_url",
                        "url":"https://www.google.com",
                        "title":"Google"
                    },
                    {
                        "type":"postback",
                        "title":"Call Postback",
                        "payload":"Payload for send_button_message()"
                    }
                    ]
                }
            }
        }
    })

    log("sending button to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def send_share_message(recipient_id):

    # Share button only works with Generic Template
    message_data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "attachment": {
                "type":"template",
                "payload":{
                    "template_type":"generic",
                    "elements":[
                    {
                        "title":"Reddit link",
                        "subtitle":"Something funny or interesting",
                        "image_url":"https://pbs.twimg.com/profile_images/667516091330002944/wOaS8FKS.png",
                        "buttons":[
                        {
                            "type":"element_share"
                        }
                        ]
                    }    
                    ]
                }
        
            }
        }
    })

    log("sending share button to {recipient}: ".format(recipient=recipient_id))

    call_send_api(message_data)


def received_postback(event):

    sender_id = event["sender"]["id"]        # the facebook ID of the person sending you the message
    recipient_id = event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

    # The payload param is a developer-defined field which is set in a postback
    # button for Structured Messages
    payload = event["postback"]["payload"]

    log("received postback from {recipient} with payload {payload}".format(recipient=recipient_id, payload=payload))

    if payload == 'Get Started':
        # Get Started button was pressed
        send_text_message(sender_id, "Welcome to SoCal Echo Bot! Anything you type will be echoed back to you, except for some keywords.")
    else:
        # Notify sender that postback was successful
        send_text_message(sender_id, "Postback called")


def call_send_api(message_data):

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=message_data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print(message)
	sys.stdout.flush()

# import os, sys
# from flask import Flask, request
# from utils import wit_response, get_news_elements
# from pymessenger import Bot
# import requests,json

# app = Flask(__name__)

# bot = Bot(os.environ["PAGE_ACCESS_TOKEN"])
# PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')


# @app.route('/', methods=['GET'])
# def verify():
# 	# Webhook verification
#     if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
#         if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
#             return "Verification token mismatch", 403
#         return request.args["hub.challenge"], 200
#     return "Hello world", 200


# @app.route('/', methods=['POST'])
# def webhook():
# 	data = request.get_json()
# 	log(data)

# 	if data['object'] == 'page':
# 		for entry in data['entry']:
# 			for messaging_event in entry['messaging']:

# 				# IDs
# 				sender_id = messaging_event['sender']['id']
# 				recipient_id = messaging_event['recipient']['id']

# 				if messaging_event.get('message'):
# 					# Extracting text message
# 					if 'text' in messaging_event['message']:
# 						messaging_text = messaging_event['message']['text']
# 					else:
# 						messaging_text = 'no text'

# 					# Echo
# 					#response = messaging_text
					
# 					# response = None
# 					# entity, value = wit_response(messaging_text)
					
# 					# if entity == 'newstype':
# 					# 	response = "OK. I will send you {} news".format(str(value))
# 					# elif entity == 'location':
# 					# 	response = "OK. So, you live in {0}. I will send you top headlines from {0}".format(str(value))
					
# 					# if response == None:
# 					# 	response = "Sorry, I didn't understand"

# 					categories = wit_response(messaging_text)
# 					elements = get_news_elements(categories)
# 					bot.send_generic_message(sender_id, elements)
				
# 				elif messaging_event.get('postback'):
# 					# HANDLE POSTBACKS HERE
# 					payload = messaging_event['postback']['payload']
# 					if payload ==  'SHOW_HELP':
# 						bot.send_quickreply(sender_id, HELP_MSG, news_categories)

# 	return "ok", 200

# def set_greeting_text():
# 	headers = {
# 		'Content-Type':'application/json'
# 		}
# 	data = {
# 		"setting_type":"greeting",
# 		"greeting":{
# 			"text":"Hi {{user_first_name}}! I am a news bot"
# 			}
# 		}
# 	ENDPOINT = "https://graph.facebook.com/v2.8/me/thread_settings?access_token=%s"%(PAGE_ACCESS_TOKEN)
# 	r = requests.post(ENDPOINT, headers = headers, data = json.dumps(data))
# 	print(r.content)

# def set_persistent_menu():
# 	headers = {
# 		'Content-Type':'application/json'
# 		}
# 	data = {
# 		"setting_type":"call_to_actions",
# 		"thread_state" : "existing_thread",
# 		"call_to_actions":[
# 			{
# 				"type":"web_url",
# 				"title":"Meet Asylex",
# 				"url":"https://asylex.ch" 
# 			},
# 			{
# 				"type":"postback",
# 				"title":"Help",
# 				"payload":"SHOW_HELP"
# 			}]
# 		}
# 	ENDPOINT = "https://graph.facebook.com/v2.8/me/thread_settings?access_token=%s"%(PAGE_ACCESS_TOKEN)
# 	r = requests.post(ENDPOINT, headers = headers, data = json.dumps(data))
# 	print(r.content)



# def log(message):
# 	print(message)
# 	sys.stdout.flush()

# set_persistent_menu()
# set_greeting_text()

# if __name__ == "__main__":
#     app.run(debug = True)