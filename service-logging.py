'''
UrlTagging Logging
Willie Chew 
2020
'''

import io
import os
import sys
import pika
import redis
import hashlib


redisHost = os.getenv("REDIS_HOST") or "localhost"

class RabbitHandler(object):
	def __init__(self, consumingExchange):
		self.rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

		# init variable
		self.rabbitMQ = pika.BlockingConnection(
				pika.ConnectionParameters(host=self.rabbitMQHost))
		self.rabbitMQChannel = self.rabbitMQ.channel()

		# bind and consume
		self.rabbitMQChannel.queue_declare('', exclusive=True)
		self.rabbitMQChannel.queue_bind(exchange=consumingExchange, queue='', routing_key='a')
		self.rabbitMQChannel.basic_consume(
			queue='',
			on_message_callback=self.on_response,
			auto_ack=True)
		self.rabbitMQChannel.start_consuming()

	def on_response(self, ch, method, props, body):
		print(body);
		# append to file aswell

rabbitmq = RabbitHandler('logging')