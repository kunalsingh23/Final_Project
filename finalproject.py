import requests
import json
import sqlite3


fb_token = 'EAACEdEose0cBAJ8EbTBHTnQBjWSiAivAFryBxAtpZAlRVM7VvCLgcn4gr7lZAfnUkwlpUuFLVDpZCTUTjUweZCuTm1ncOmbGjxnIY4tqT4MGbHgADnY2BaM500zuMribCgOeI9YfsHK60hZCbNrMMUxjZBxV1XorWFG8dBkbCsoT97a6zk6yiitwlGXX07qrMZD'
#token expires often, but data is cached for this class so we don't have to keep calling the data

FB_Cache = "facebook_cache.json"
try:
    fb_file = open(FB_Cache, 'r')
    fb_contents = fb_file.read()
    fb_file.close()
    FB_Diction = json.loads(fb_contents)
except:
    FB_Diction = {}

def request_fb():
	request = 'me?fields=likes.limit(100)'  #used the Graph API, change the request to get different data 
	
	if request in FB_Diction:
		print ('Cached!')
		return (FB_Diction[request])

	else:
		print ('Requesting Graph API')
		r = requests.get('https://graph.facebook.com/v2.11/' + request, {'access_token' : fb_token})
		fbdata = r.json()
		try:
			FB_Diction[request] = fbdata      #key is the request, value is the data
			fbdump = json.dumps(FB_Diction)
			fw = open(FB_Cache, 'w')
			fw.write(fbdump)
			return (fbdump)
			fw.close()

		except:
			return ('Problem Caching')

fbdata = request_fb()

month_count = {}

for x in fbdata['likes']['data']:
	timestamp = (x['created_time'])
	month = timestamp.split('-')[1]
	
	if month in month_count:
		month_count[month] += 1
	else:
		month_count[month] = 1

conn = sqlite3.connect('final_project.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Facebook_Data')

cur.execute('''CREATE TABLE Facebook_Data (name TEXT, id INTEGER, time TIMESTAMP)''') #making table for all facebook data

for x in fbdata['likes']['data']:
	cur.execute("INSERT OR IGNORE INTO Facebook_Data (name, id, time) VALUES (?, ?, ?)",
		(x['name'], x['id'],x['created_time']))

conn.commit()







