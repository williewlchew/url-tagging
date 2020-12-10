'''
UrlTagging Linking
Willie Chew 
2020
'''

import io, os, sys, pika, redis, hashlib, requests, warnings, mysql.connector
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA
import numpy as np
from collections import Counter

import protos.links_pb2 as linksPb


redisHost = os.getenv("REDIS_HOST") or "localhost"
rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
mysqlHost = os.getenv("MYSQL_HOST") or "localhost"


### Linker RabbitMQ
#################################
class RabbitHandler(object):
	def __init__(self, consumingExchange, publishingExchange):
		# init variables
		self.rabbitMQHost = os.getenv("RABBITMQ_HOST") or "localhost"
		self.rabbitMQ = pika.BlockingConnection(
				pika.ConnectionParameters(host=self.rabbitMQHost))
		self.rabbitMQChannel = self.rabbitMQ.channel()
		self.publishingExchange = publishingExchange
		self.linkRequestHandler = LinkRequestHandler()

		# bind and consume
		self.rabbitMQChannel.queue_declare('', exclusive=True)
		self.rabbitMQChannel.queue_bind(exchange=consumingExchange, queue='', routing_key='a')
		self.rabbitMQChannel.basic_consume(
			queue='',
			on_message_callback=self.on_response,
			auto_ack=True)
		self.rabbitMQChannel.start_consuming()

	def on_response(self, ch, method, props, body):
		# Get content from url
		linkResults = self.linkRequestHandler.GetUrlContent(body)
		link = linkResults[0]
		print(link)
		message = link.SerializeToString()
		self.rabbitMQChannel.basic_publish(exchange=self.publishingExchange, body=message, routing_key='b', properties=pika.BasicProperties(correlation_id = 'c'))
		
		logMessage = linkResults[1][0]
		if(logMessage != 'cache hit'):
			self.log("[linker] link recieved: " + link.url)

			# Scrape link contents
			result = self.linkRequestHandler.ProcessContent(linkResults[0], linkResults[1])
			self.log("[linker] link scrape success: " + result + " " + link.url)
		else:
			self.log("[linker] link cache hit: " + link.url)

	def log(self, message):
		self.rabbitMQChannel.basic_publish(exchange='logging', body=message, routing_key='a')


### Logic for handling requests
#################################
class LinkRequestHandler(object):
	def __init__(self):
		self.linkProcessor = LinkProcessor()
		self.redisCache = RedisCache()
		self.sqlDatabase = SqlDatabase()

	def GetUrlContent(self, message):
		link = linksPb.Link()
		link.ParseFromString(message) # try catch

		# Check cache
		hashCheck = self.redisCache.Get(link.url)
		if (hashCheck != None):
			link.ParseFromString(hashCheck)
			return (link, ['cache hit'])

		# Get content from url
		linkContent = self.linkProcessor.Process(link.url)
		linkContent = [i for i in linkContent if i] 
		if(linkContent[0] == "error"):
			link.tags[:] = ['unable to get content from url']
		else:
			link.tags[:] = ['currently processing']
		return (link, linkContent)

	def ProcessContent(self, link, linkContent):
		try:
			resultTags = self.linkProcessor.Tag(linkContent, 8,15)

			# Cache in key-value store
			link.tags[:] = resultTags
			self.redisCache.Set(link.url, link.SerializeToString())

			# Put tags in data base 
			self.sqlDatabase.AddEntry(link)

			return "1"
		
		except Exception as e:
			print(e)
			return "0"


### Redis Caching
#################################
class RedisCache(object):
	def __init__(self):
		self.redisStore = redis.Redis(host=redisHost, db=0)
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

		mycursor = self.mydb.cursor()

		try:
			mycursor.execute("CREATE TABLE links (url_id VARCHAR(255), url VARCHAR(255))")
		except:
			mycursor.execute("TRUNCATE TABLE links")
		try:
			mycursor.execute("CREATE TABLE tags (tag_id VARCHAR(255), tag VARCHAR(255))")
		except:
			mycursor.execute("TRUNCATE TABLE tags")
		try:
			mycursor.execute("CREATE TABLE link_tag (url_id VARCHAR(255), tag_id VARCHAR(255))")
		except:
			mycursor.execute("TRUNCATE TABLE link_tag")

	def AddEntry(self, link):
		mycursor = self.mydb.cursor()
		# Add to links table
		sql = "INSERT INTO links (url_id, url) VALUES (%s, %s)"
		key = hashlib.sha224(bytes(link.url, 'utf-8')).hexdigest()
		val = (key, link.url)
		mycursor.execute(sql, val)

		for tag in link.tags[:]:
			# Add to tags table
			sql = "INSERT INTO link_tag (url_id, tag_id) VALUES (%s, %s)"
			tagId = hashlib.sha224(bytes(tag, 'utf-8')).hexdigest()
			val = (key, tagId)
			mycursor.execute(sql, val)

			# Add to link_tag table
			sql = "INSERT INTO tags (tag_id, tag) VALUES (%s, %s)"
			tagId = hashlib.sha224(bytes(tag, 'utf-8')).hexdigest()
			val = (tagId, tag)
			mycursor.execute(sql, val)

		self.mydb.commit()




### URL Processing and Scraping
### parts of code from: https://towardsdatascience.com/end-to-end-topic-modeling-in-python-latent-dirichlet-allocation-lda-35ce4ed6b3e0
#################################
class LinkProcessor(object): 
	def __init__(self):
		warnings.simplefilter("ignore", DeprecationWarning)

	# Retrieve and Scrape
	def Process(self, url):
		try:
			urlResponse = requests.get(url)
			soup = BeautifulSoup(urlResponse.content, 'html.parser')
			allP = soup.find_all('p')
			allP = list(map(lambda p: p.string, allP))
			return(allP)
		except Exception as err:
			return["error", err]

	# Find tags
	def Tag(self, content, numberTopics, numberWords):
		lda = LDA(n_components=numberTopics, n_jobs=-1)
		countData = self.GetCountData(content)

		topics = []
		for i in range(3):
			lda.fit(countData[0])
			iterationTopics = self.FitLDA(lda, countData[1], numberWords)
			topics.extend(iterationTopics)

		return self.ExtractTagsFromTopics(topics)

	def GetCountData(self, docs):
		count_vectorizer = CountVectorizer(stop_words='english')
		count_data = count_vectorizer.fit_transform(docs)

		return (count_data, count_vectorizer)

	def FitLDA(self, model, count_vectorizer, n_top_words):
		words = count_vectorizer.get_feature_names()
		ret = []
		for topic_idx, topic in enumerate(model.components_):
			ret.append(" ".join([words[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))
		return ret

	def ExtractTagsFromTopics(self, topics):
		topics = " ".join(topics)
		words = topics.split(" ")
		results = Counter(words).most_common(10)
		keys = list(map(lambda x: x[0], results))
		return keys

def main():
	if(len(sys.argv) == 1):
		rabbitmq = RabbitHandler('linkReq', 'response')

	# Testing
	else: 
		print("Testing Linker Component:")
		linkProcessor = LinkProcessor()
		url = 'https://www.motorsport.com/f1/news/racing-point-didnt-have-enough-spares-after-bahrain-clashes/4923611/'
		pageContent = linkProcessor.Process(url)
		tags = linkProcessor.Tag(pageContent, 8, 15)
		print(tags)

if __name__ == "__main__":
    main()