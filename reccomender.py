'''
UrlTagging Reccomending
Willie Chew 
2020
'''
import io, os, sys, pika, redis, hashlib, mysql.connector
import protos.links_pb2 as linksPb

redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
mysqlHost = os.getenv("MYSQL_HOST") or "localhost"

class RabbitHandler(object):
	def __init__(self, consumingExchange, publishingExchange):
		# init variable
		self.rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
		self.rabbitMQ = pika.BlockingConnection(
				pika.ConnectionParameters(host=self.rabbitMQHost))
		self.rabbitMQChannel = self.rabbitMQ.channel()
		self.publishingExchange = publishingExchange
		self.reccRequestHandler = ReccRequestHandler()

		# bind and consume
		self.rabbitMQChannel.queue_declare('', exclusive=True)
		self.rabbitMQChannel.queue_bind(exchange=consumingExchange, queue='', routing_key='a')
		self.rabbitMQChannel.basic_consume(
			queue='',
			on_message_callback=self.on_response,
			auto_ack=True)
		self.rabbitMQChannel.start_consuming()

	def on_response(self, ch, method, props, body):
		# Recieve message
		recc = self.reccRequestHandler.ProcessMessage(body)
		print(recc)
		self.log("[reccomender] reccomend success: " + ",".join(recc.inputTags[:]))

		# Send results back
		message = recc.SerializeToString()
		self.rabbitMQChannel.basic_publish(exchange=self.publishingExchange, body=message, routing_key='b', properties=pika.BasicProperties(correlation_id = 'c'))

	def log(self, message):
		self.rabbitMQChannel.basic_publish(exchange='logging', body=message, routing_key='a')

class ReccRequestHandler(object):
	def __init__(self):
		self.redisCache = RedisCache()
		self.sqlDatabase = SqlDatabase()

	def ProcessMessage(self, message):
		recc = linksPb.Reccomendation()
		recc.ParseFromString(message)

		# check cache
		hashCheck = self.redisCache.Get(''.join(recc.inputTags))
		if (hashCheck != None):
			recc.ParseFromString(hashCheck)
			return recc

		# find relevant articles
		results = self.ProcessTags(recc.inputTags)
		articles = []
		for result in results:
			newLink = linksPb.Link();
			newLink.url = result
			articles.append(newLink)
		recc.outputLinks.extend(articles)

		# cache in redis
		self.redisCache.Set(''.join(recc.inputTags), recc.SerializeToString())
		
		return recc

	def ProcessTags(self, tags):
		tagSet = "\",\"".join(tags)
		query = "SELECT tag_id FROM tags WHERE tag IN (\"" + tagSet + "\")"
		relevantTagIds = self.sqlDatabase.Query(query)
		relevantTagIds = list(map(lambda x: x[0], relevantTagIds))

		relevantTagIds = "\",\"".join(relevantTagIds)
		query = "SELECT url_id FROM link_tag WHERE tag_id IN (\"" + relevantTagIds + "\")"
		relevantUrlIds = self.sqlDatabase.Query(query)
		relevantUrlIds = list(map(lambda x: x[0], relevantUrlIds))

		relevantUrlIds = "\",\"".join(relevantUrlIds)
		query = "SELECT DISTINCT url FROM links WHERE url_id IN (\"" + relevantUrlIds + "\")"
		results = self.sqlDatabase.Query(query)
		results = list(map(lambda x: x[0], results))
		
		return results


### Redis Caching
#################################
class RedisCache(object):
	def __init__(self):
		self.redisStore = redis.Redis(host=redisHost, db=1)
		self.redisStore.flushdb()
	
	def Set(self, key, value):
		key = hashlib.sha224(bytes(key, 'utf-8')).hexdigest()
		self.redisStore.set(key, value)

	def Get(self, key):
		key = hashlib.sha224(bytes(key, 'utf-8')).hexdigest()
		return self.redisStore.get(key)

### MySql Database
#################################
class SqlDatabase(object):
	def __init__(self):
		self.mydb = mysql.connector.connect(
		  host=mysqlHost,
		  port="3306",
		  user="root",
		  password="password",
		  database="mydatabase"
		)

	def Query(self, query):
		mycursor = self.mydb.cursor()
		mycursor.execute(query)
		return(mycursor.fetchall())

class ReccProcessor(object): 
	def Process(self, tags):
		#wip
		link1 = linksPb.Link();
		link1.url = 'l1'
		link2 = linksPb.Link();
		link2.url = 'l2'
		link3 = linksPb.Link();
		link3.url = 'l3'
		return [link1, link2, link3]


reccProcessor = ReccProcessor()
rabbitmq = RabbitHandler('reccReq', 'response')