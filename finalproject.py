import requests
import json
import sqlite3
import plotly
from plotly.graph_objs import Bar, Layout #, Scatter
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.plotly as py
from bs4 import BeautifulSoup
# 													PART 1, FACEBOOK API

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
		print ('Facebook Cached!')
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

month_numbers_count = {}
month_count = {}

for x in fbdata['likes']['data']:
	timestamp = (x['created_time'])
	month = timestamp.split('-')[1]
	
	if month in month_numbers_count:
		month_numbers_count[month] += 1
	else:
		month_numbers_count[month] = 1

for x in month_numbers_count:
	if x == '01':
		month_count['Jan'] = month_numbers_count[x]
	if x == '02':
		month_count['Feb'] = month_numbers_count[x]
	if x == '03':
		month_count['March'] = month_numbers_count[x]
	if x == '04':
		month_count['April'] = month_numbers_count[x]
	if x == '05':
		month_count['May'] = month_numbers_count[x]
	if x == '06':
		month_count['June'] = month_numbers_count[x]
	if x == '07':
		month_count['July'] = month_numbers_count[x]
	if x == '08':
		month_count['Aug'] = month_numbers_count[x]
	if x == '09':
		month_count['Sept'] = month_numbers_count[x]
	if x == '10':
		month_count['Oct'] = month_numbers_count[x]
	if x == '11':
		month_count['Nov'] = month_numbers_count[x]
	if x == '12':
		month_count['Dec'] = month_numbers_count[x]

conn = sqlite3.connect('final_project.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Facebook_Data')

cur.execute('''CREATE TABLE Facebook_Data (name TEXT, id INTEGER, time TIMESTAMP)''') #making table for all facebook data

for x in fbdata['likes']['data']:
	cur.execute("INSERT OR IGNORE INTO Facebook_Data (name, id, time) VALUES (?, ?, ?)",
		(x['name'], x['id'],x['created_time']))

conn.commit()

months = []
count_months = []

for x in month_count.keys():
	months.append(x)

for x in month_count.values():
	count_months.append(x)

months = sorted(months, key = lambda x: month_count[x], reverse = True)
count_months = sorted(count_months, reverse = True)

# plotly.offline.plot({
# 	"data": [Bar(x= months, y= count_months)],
# 	"layout": Layout(title = 'Facebook Likes by Month')
# 	})




#													PART 2, GOOGLE MAPS API


Maps_Cache = "Maps.json"
try:
    maps_file = open(Maps_Cache, 'r')
    maps_contents = maps_file.read()
    maps_file.close()
    maps_Diction = json.loads(maps_contents)
except:
    Maps_Diction = {}


base_url = 'https://www.worldstadiumdatabase.com/top-100-capacity-stadiums.htm'
r = requests.get(base_url)
soup = BeautifulSoup(r.text, 'lxml')

string = ' '

for x in (soup.find_all(class_ = "table table-striped")):
	string = x.text

lst = (string.split('\n'))
newlst = []
for x in lst:
	if x != '':
		newlst.append(x)

newlst = (newlst[5:])

stadiums = (newlst[1::5])

stadiumlzt = []

for name in stadiums:
	if (name != 'Soccer City') and (name != "Tiger Stadium") and (name != 'Castelao') and (name != 'Citrus Bowl') and (name != 'Stadio delle Alpi'):
		stadiumlzt.append([name])
	elif name == 'Soccer City':
		stadiumlzt.append(['FNB Stadium'])
	elif name == "Tiger Stadium":
		stadiumlzt.append(['LSU Stadium'])
	elif name == 'Castelao':
		stadiumlzt.append(['Castelao Stadium'])
	elif name == 'Citrus Bowl':
		stadiumlzt.append(['Camping World Stadium'])
	elif name == 'Stadio delle Alpi':
		stadiumlzt.append(['Stadio delle Alpi Torino'])


def get_timezone(lst):
	
	Maps_Diction = (json.loads(open("Maps.json").read()))
	check = lst[0]
	check = str(check[0])

	if len(Maps_Diction) == 98:
		print ('Coordinates Cached!')
				
	else:
		print ('Requesting Google Maps API')

		coord_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query='
		key = 'AIzaSyA08it_eqs8q8Uy5sLVatGf5qbyqoE-fHc'

		for name in lst:
			stadium = name[0]

			url = coord_url + stadium + '&key=' + key 

			data = requests.get(url)

			data = data.json()
		
			lat = (str(data['results'][0]['geometry']['location']['lat']))
			lng = (str(data['results'][0]['geometry']['location']['lng']))

			coord = (lat + ',' + lng)

			name.append(coord)
			
			Maps_Diction[name[0]] = {'Coordinates': name[1]}

		try:
			mapsdump = json.dumps(Maps_Diction)
			fw = open(Maps_Cache, 'w')
			fw.write(mapsdump)
			fw.close()
		except:
			return ('Invalid Request')

	timezone_url = 'https://maps.googleapis.com/maps/api/timezone/json?location='
	key2 = 'AIzaSyCbkRfoH9mPRUBtAmYVdug22fPRzQlf1hA'
	timestamp = '1512475200'

	if len(Maps_Diction[check]) > 1:
		print ('Timezone Cached!')
		return (Maps_Diction)


	for x in Maps_Diction:

		stadium = x
		coord = Maps_Diction[x]['Coordinates']

		url = timezone_url + coord + '&timestamp=' + timestamp + '&key=' + key2

		data = requests.get(url)

		data = data.json()

		timezone = data['timeZoneName']
		
		Maps_Diction[x] = {'Coordinates': coord, 'TimeZone': timezone, 'Data': data}

	try:
		mapsdump = json.dumps(Maps_Diction)
		fw = open(Maps_Cache, 'w')
		fw.write(mapsdump)
		return (mapsdump)
		fw.close()
	except:
		return ('Invalid Request')

stadium_timezones = (get_timezone(stadiumlzt))

timezonecount = {}

for x in stadium_timezones:
	if (stadium_timezones[x]['TimeZone']) not in timezonecount:
		timezonecount[stadium_timezones[x]['TimeZone']] = 1
	else:
		timezonecount[stadium_timezones[x]['TimeZone']] += 1


cur.execute('DROP TABLE IF EXISTS Maps_Data')

cur.execute('''CREATE TABLE Maps_Data (stadium TEXT, coordinates INTEGER, timezone TIMESTAMP)''')

for x in stadium_timezones:
	cur.execute("INSERT OR IGNORE INTO Maps_Data (stadium, coordinates, timezone) VALUES (?, ?, ?)",
		(x, (stadium_timezones[x]['Coordinates']), (stadium_timezones[x]['TimeZone'])))

conn.commit()


#														PART 3, ITUNES API


iTunes_Cache = "iTunes_cache.json"
try:
    iTunes_file = open(iTunes_Cache, 'r')
    iTunes_contents = iTunes_file.read()
    iTunes_file.close()
    iTunes_Diction = json.loads(iTunes_contents)
except:
    iTunes_Diction = {}


def iTunes(artist):
	if artist in iTunes_Diction:
		print ('iTunes Cached!')
		return (iTunes_Diction)

	else:
		print ('Requesting iTunes')
	
		x = requests.get('http://itunes.apple.com/search', params = {
    		"term": artist,
    		"entity": "song",
    		"limit": "100" })

		itunesdata = x.json()

		try:
			iTunes_Diction[artist] = itunesdata    
			iTunesdump = json.dumps(iTunes_Diction)
			fw = open(iTunes_Cache, 'w')
			fw.write(iTunesdump)
			return (iTunesdump)
			fw.close()

		except:
			return ('Problem Caching')



iTunesData = (iTunes('Drake'))

mydata = {}

for y in (iTunesData['Drake']['results']):
	
	mydata[y['trackName']] = {'TrackLength': (y['trackTimeMillis'])/1000, 'Release Year': y['releaseDate']}

lengths = []
years = []

for x in mydata:
	lengths.append(mydata[x]['TrackLength'])
	two = (mydata[x]['Release Year'])
	two = two.split('T')[0]
	two = int(two[:4])
	years.append(two)




cur.execute('DROP TABLE IF EXISTS iTunes_Data')

cur.execute('''CREATE TABLE iTunes_Data (song TEXT, length INTEGER, created_time TIMESTAMP)''')

for x in (iTunesData['Drake']['results']):
	cur.execute("INSERT OR IGNORE INTO iTunes_Data (song, length, created_time) VALUES (?, ?, ?)",
		(x['trackName'], (x['trackTimeMillis']/1000), (x['releaseDate'])))

conn.commit()



