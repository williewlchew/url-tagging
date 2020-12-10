'''
UrlTagging Routing
Willie Chew 
2020
'''

from flask import Flask, request, Response
import json, pickle, platform, io, os, sys, pika, redis, hashlib, requests

import protos.links_pb2 as linksPb

### Initialize Connections
#################################
#################################
# Configure test vs. production
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"


### RabbitMQ
#################################
#################################
class RabbitHandler(object):
	def __init__(self):
		# init variable
		self.rabbitMQ = pika.BlockingConnection(
				pika.ConnectionParameters(host=rabbitMQHost))
		self.rabbitMQChannel = self.rabbitMQ.channel()
		self.corr_id = 'c'
		self.response = None

		# set up exchanges
		self.rabbitMQChannel.exchange_declare(exchange='logging', exchange_type='direct')
		self.rabbitMQChannel.exchange_declare(exchange='reccReq', exchange_type='direct')
		self.rabbitMQChannel.exchange_declare(exchange='linkReq', exchange_type='direct')
		self.rabbitMQChannel.exchange_declare(exchange='reccRes', exchange_type='direct')
		self.rabbitMQChannel.exchange_declare(exchange='linkRes', exchange_type='direct')
		self.rabbitMQChannel.exchange_declare(exchange='response', exchange_type='direct')

		# listen to response queue
		self.rabbitMQChannel.queue_declare('', exclusive=True)
		self.rabbitMQChannel.queue_bind(exchange='response', queue='', routing_key='b')

		self.rabbitMQChannel.basic_consume(
			queue='',
			on_message_callback=self.on_response,
			auto_ack=True)

	def PlaceInQueue(self, exchange, message):
		self.rabbitMQChannel.basic_publish(exchange=exchange, body=message, routing_key='a')
		self.response = None

	def GetRequestUpdate(self, exchange):
		while(self.response is None):
			self.rabbitMQ.process_data_events()

		return self.response

	def on_response(self, ch, method, props, body):
		if self.corr_id == props.correlation_id:
			print(body)
			self.response = body


rabbitmq = RabbitHandler()


### Flask End-Points
#################################
#################################
app = Flask(__name__)



### Endpoint for index
#################################
@app.route('/', methods=['GET'])
def indexEndpoint():
	response = {'working' : 'true'}
	return Response(response=json.dumps(response).encode('utf-8') , status=200, mimetype="application/json")



### Endpoint for link
#################################
@app.route('/link', methods=['POST'])
def LinkEndpoint():
	r = request.get_json()
	url = r.get('url')

	# establish link proto
	link = linksPb.Link()
	try:	
		link.url = url
	except:
		response = {'result' : 'failed'}
		return Response(response=json.dumps(response).encode('utf-8') , status=200, mimetype="application/json")

	# put in queue to be processed
	rabbitmq.PlaceInQueue('logging', "[routing] request to linker: " + url)
	rabbitmq.PlaceInQueue('linkReq', link.SerializeToString()) 

	# await confirmation
	link.ParseFromString(rabbitmq.GetRequestUpdate('linkRes'))

	response = {'result' : link.tags[:]}
	return Response(response=json.dumps(response).encode('utf-8') , status=200, mimetype="application/json")



### Endpoint for reccomend
#################################
@app.route('/reccomend', methods=['POST'])
def ReccEndpoint():
	r = request.get_json()
	tags = r.get('tags')

	# establish link proto
	recc = linksPb.Reccomendation()

	try:	
		recc.inputTags[:] = tags.split('+')
	except:
		response = {'result' : 'failed'}
		return Response(response=json.dumps(response).encode('utf-8') , status=200, mimetype="application/json")

	# put in queue to be processed
	rabbitmq.PlaceInQueue('logging', "[routing] request to reccomender: " + tags)
	rabbitmq.PlaceInQueue('reccReq', recc.SerializeToString()) 

	# await confirmation
	recc.ParseFromString(rabbitmq.GetRequestUpdate('reccRes'))

	response = {'result' : LinksToList(recc.outputLinks[:])}
	return Response(response=json.dumps(response).encode('utf-8') , status=200, mimetype="application/json")

def LinksToList(links):
	ret = []
	for link in links:
		entry = {
			'url' : link.url,
			'tags' : link.tags[:]
		}
		ret.append(entry)
	return ret

# start flask app
app.run(host="0.0.0.0", port=5000)