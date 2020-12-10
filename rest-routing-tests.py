import jsonpickle, pickle
import platform
from PIL import Image
import io
import os
import sys
import pika
import redis
import hashlib
import face_recognition

# initializa rabbit parameters
redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"

print("Connecting to rabbitmq({}) and redis({})".format(rabbitMQHost,redisHost))

rabbitMQ = pika.BlockingConnection(
		pika.ConnectionParameters(host=rabbitMQHost))
rabbitMQChannel = rabbitMQ.channel()

rabbitMQChannel.queue_declare('', exclusive=True)
rabbitMQChannel.queue_bind(exchange='linkReq', queue='', routing_key='a')


def callback(ch, method, properties, body):
	# test routing publish
	print(body)

	# test routing consume
	rabbitMQChannel.basic_publish(exchange='linkRes', body=body, routing_key='b', properties=pika.BasicProperties(correlation_id = 'c'))

# establish routing
rabbitMQChannel.basic_consume(queue='', on_message_callback=callback, auto_ack=True)
rabbitMQChannel.start_consuming()