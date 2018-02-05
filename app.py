import os, sys
from flask import Flask, request
from utils import wit_response, get_news_elements
from pymessenger import Bot
import requests,json

app = Flask(__name__)

bot = Bot(os.environ["PAGE_ACCESS_TOKEN"])
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')


@app.route('/', methods=['GET'])
def verify():
	# Webhook verification
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
	data = request.get_json()
	log(data)

	if data['object'] == 'page':
		for entry in data['entry']:
			for messaging_event in entry['messaging']:

				# IDs
				sender_id = messaging_event['sender']['id']
				recipient_id = messaging_event['recipient']['id']

				if messaging_event.get('message'):
					# Extracting text message
					if 'text' in messaging_event['message']:
						messaging_text = messaging_event['message']['text']
					else:
						messaging_text = 'no text'

					# Echo
					#response = messaging_text
					
					# response = None
					# entity, value = wit_response(messaging_text)
					
					# if entity == 'newstype':
					# 	response = "OK. I will send you {} news".format(str(value))
					# elif entity == 'location':
					# 	response = "OK. So, you live in {0}. I will send you top headlines from {0}".format(str(value))
					
					# if response == None:
					# 	response = "Sorry, I didn't understand"

					categories = wit_response(messaging_text)
					elements = get_news_elements(categories)
					bot.send_generic_message(sender_id, elements)

	return "ok", 200

def set_greeting_text():
	headers = {
		'Content-Type':'application/json'
		}
	data = {
		"setting_type":"greeting",
		"greeting":{
			"text":"Hi {{user_first_name}}! I am a news bot"
			}
		}
	ENDPOINT = "https://graph.facebook.com/v2.8/me/thread_settings?access_token=%s"%(PAGE_ACCESS_TOKEN)
	r = requests.post(ENDPOINT, headers = headers, data = json.dumps(data))
	print(r.content)


def log(message):
	print(message)
	sys.stdout.flush()

set_greeting_text()

if __name__ == "__main__":
    app.run(debug = True)