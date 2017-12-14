import requests
import json
import sqlite3
import plotly
from plotly.graph_objs import Bar, Layout, Scatter, Pie
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.plotly as py
from bs4 import BeautifulSoup
import datetime
#										PART 1, FACEBOOK API

fb_token = 'EAACEdEose0cBAJ8EbTBHTnQBjWSiAivAFryBxAtpZAlRVM7VvCLgcn4gr7lZAfnUkwlpUuFLVDpZCTUTjUweZCuTm1ncOmbGjxnIY4tqT4MGbHgADnY2BaM500zuMribCgOeI9YfsHK60hZCbNrMMUxjZBxV1XorWFG8dBkbCsoT97a6zk6yiitwlGXX07qrMZD'
#token expires often, but data is cached so we don't have to keep calling the data

FB_Cache = "facebook_cache.json" #setting up cache
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
		fbdata = r.json() 	#gets data from facebook and puts it in json format so we can use it
		try:
			FB_Diction[request] = fbdata      #key is the request, value is the data
			fbdump = json.dumps(FB_Diction)
			fw = open(FB_Cache, 'w')
			fw.write(fbdump)
			return (fbdump)
			fw.close()

		except:
			return ('Problem Caching')

fbdata = request_fb()			#variable for our request 
timestamps = []

for dic in (fbdata['likes']['data']):
	timestamps.append(dic['created_time'])			#list of timestamps

timeofday = {}						#dictionary for time of day
timeofday["Midnight-5:59AM"] = 0
timeofday["6AM-11:59AM"] = 0
timeofday["Noon-5:59PM"] = 0
timeofday["6PM-11:59PM"] = 0

dayofweek = {}					#dictionary for day of the week
dayofweek['Monday'] = 0
dayofweek['Tuesday'] = 0
dayofweek['Wednesday'] = 0
dayofweek['Thursday'] = 0
dayofweek['Friday'] = 0
dayofweek['Saturday'] = 0
dayofweek['Sunday'] = 0

for timestamp in timestamps:
	date = timestamp.split('T')[0]
	time = timestamp.split('T')[1][:-5]

	year = (int(date[:4]))
	month = date[5:7]
	if month[0] == '0':
		month = month[1]
	else:
		month = month
	month = int(month)

	day = date[8:]
	if day[0] == '0':
		day = day[1]
	else:
		day = day
	day = int(day)

	day_of_week = datetime.datetime(year,month,day).weekday()		#use datetime module to get day of week

	if day_of_week == 0:					#getting day of week count
		dayofweek['Monday'] += 1
	if day_of_week == 1:
		dayofweek['Tuesday'] += 1
	if day_of_week == 2:
		dayofweek['Wednesday'] += 1
	if day_of_week == 3:
		dayofweek['Thursday'] += 1
	if day_of_week == 4:
		dayofweek['Friday'] += 1
	if day_of_week == 5:
		dayofweek['Saturday'] += 1
	if day_of_week == 6:
		dayofweek['Sunday'] += 1

	hour = (int(time[0:2]))

	if (hour >= 0) and (hour <= 5):				#counting when I'm most active by 4 hour segments 
		timeofday["Midnight-5:59AM"] += 1
	if (hour >= 6) and (hour <= 11):
		timeofday["6AM-11:59AM"] += 1
	if (hour >= 12) and (hour <= 17):
		timeofday["Noon-5:59PM"] += 1
	if (hour >= 18):
		timeofday["6PM-11:59PM"] += 1


conn = sqlite3.connect('Facebook.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Facebook_Data')

cur.execute('''CREATE TABLE Facebook_Data (name TEXT, id INTEGER, time TIMESTAMP)''') #making table for facebook data

for x in fbdata['likes']['data']:
	cur.execute("INSERT OR IGNORE INTO Facebook_Data (name, id, time) VALUES (?, ?, ?)",
		(x['name'], x['id'],x['created_time'])) #storing name, ID, timestamp 

conn.commit()


#uncomment for below visualization, should open in plotly on your computer (offline plot.ly)

# plotly.offline.plot({					
# 	"data": [Bar(x= list(dayofweek.keys()), y= list(dayofweek.values()))],		
# 	"layout": Layout(title = 'Facebook Likes by Day of Week',
# 					xaxis = dict(title='Day of Week'),
# 					yaxis = dict(title = 'Number of Likes'))
# 	})

# #uncomment below for visualization, should open in plotly on your computer (offline plot.ly)

# plotly.offline.plot({
# 	"data" : [Pie(labels = list(timeofday.keys()), values = list(timeofday.values()))],
# 	"layout": Layout(title = "When am I liking on Facebook?")
# 	})

#										PART 2, GOOGLE MAPS API


Maps_Cache = "Maps.json"			#setting up cache
try:
    maps_file = open(Maps_Cache, 'r')
    maps_contents = maps_file.read()
    maps_file.close()
    Maps_Diction = json.loads(maps_contents)
except:
    Maps_Diction = {}


base_url = 'https://www.worldstadiumdatabase.com/top-100-capacity-stadiums.htm'
r = requests.get(base_url)
soup = BeautifulSoup(r.text, 'lxml')

string = ' '

for x in (soup.find_all(class_ = "table table-striped")): #scrapping data from base_url to get 100 biggest stadiums in the world
	string = x.text

lst = (string.split('\n'))
newlst = []
for x in lst:
	if x != '':
		newlst.append(x)

newlst = (newlst[5:])

stadiums = (newlst[1::5])

stadiumlzt = []

for name in stadiums: #some stadiums go by different names than their name in the table, had to make sure I got the name correct or API would be mad
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

	if len(Maps_Diction) == 100:     		#If the cache has 100 things in it go to next API
		print ('Coordinates Cached!')
				
	else:
		print ('Requesting Google Maps API')

		coord_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=' #First API in the funciton
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

	timezone_url = 'https://maps.googleapis.com/maps/api/timezone/json?location='	#second API
	key2 = 'AIzaSyCbkRfoH9mPRUBtAmYVdug22fPRzQlf1hA'
	timestamp = '1512475200'

	if len(Maps_Diction[check]) > 1:
		print ('Timezone Cached!')
		return (Maps_Diction)		#Return Cache if there are coordinates and timezone data


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

timezonecount = {}		#Count of timezones 

for x in stadium_timezones:
	if (stadium_timezones[x]['TimeZone']) not in timezonecount:
		timezonecount[stadium_timezones[x]['TimeZone']] = 1
	else:
		timezonecount[stadium_timezones[x]['TimeZone']] += 1

conn = sqlite3.connect('GoogleMaps.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Maps_Data')

cur.execute('''CREATE TABLE Maps_Data (stadium TEXT, coordinates INTEGER, timezone TIMESTAMP)''')

for x in stadium_timezones:
	cur.execute("INSERT OR IGNORE INTO Maps_Data (stadium, coordinates, timezone) VALUES (?, ?, ?)",
		(x, (stadium_timezones[x]['Coordinates']), (stadium_timezones[x]['TimeZone'])))
		# storing stadium name, stadium coordinates, stadium timezone

conn.commit()

sorttimezones = sorted(timezonecount, key =lambda  x : timezonecount[x], reverse = True)
sortedcounts = sorted(timezonecount.values(), reverse = True)

#uncomment for below visualization, should open in plotly on your computer (offline plot.ly)

# plotly.offline.plot({
# 	"data": [Bar(x= sorttimezones, y= sortedcounts)],
# 	"layout": Layout(title = '100 Biggest Stadiums in the World by TimeZone',
# 					xaxis = dict(title='TimeZone'),
# 					yaxis = dict(title = 'Number of Stadiums'))
# 	})


#										PART 3, ITUNES API

	
iTunes_Cache = "iTunes_cache.json"		#setting up iTunes cache
try:
    iTunes_file = open(iTunes_Cache, 'r')
    iTunes_contents = iTunes_file.read()
    iTunes_file.close()
    iTunes_Diction = json.loads(iTunes_contents)
except:
    iTunes_Diction = {}


def iTunes(artist):
	if artist in iTunes_Diction:		#if this specific artist has already been 
		print ('iTunes Cached!')
		return (iTunes_Diction)

	else:
		print ('Requesting iTunes')
	
		x = requests.get('http://itunes.apple.com/search', params = { 	#requesting iTunes API by these params
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



iTunesData = (iTunes('Drake'))		#saving variable for iTunes

mydata = {}

for y in (iTunesData['Drake']['results']):
	
	mydata[y['trackName']] = {'TrackLength': (y['trackTimeMillis'])/1000, 'Release Year': y['releaseDate']}		#create dictionary for song, tracklength, release year

lengths = []
years = []

for x in mydata:
	lengths.append(mydata[x]['TrackLength'])
	two = (mydata[x]['Release Year'])
	two = two.split('T')[0]
	two = int(two[:4])
	years.append(two)

conn = sqlite3.connect('iTunes.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS iTunes_Data')

cur.execute('''CREATE TABLE iTunes_Data (song TEXT, length INTEGER, created_time TIMESTAMP)''')

for x in (iTunesData['Drake']['results']):
	cur.execute("INSERT OR IGNORE INTO iTunes_Data (song, length, created_time) VALUES (?, ?, ?)",
		(x['trackName'], (x['trackTimeMillis']/1000), (x['releaseDate'])))
		# storing trackname, length of the track, and release date
conn.commit()

#makes a dictionary for every year and stores the year and the length of all the tracks from that year

_2009 = []

for x in mydata:
	releasedate = (mydata[x]['Release Year'])
	year = releasedate.split('-')[0]
	if year == '2009':
		length = mydata[x]['TrackLength']
		_2009.append(length)

_2010 = []

for x in mydata:
	releasedate = (mydata[x]['Release Year'])
	year = releasedate.split('-')[0]
	if year == '2010':
		length = mydata[x]['TrackLength']
		_2010.append(length)

_2011 = []
for x in mydata:
	releasedate = (mydata[x]['Release Year'])
	year = releasedate.split('-')[0]
	if year == '2011':
		length = mydata[x]['TrackLength']
		_2011.append(length)

_2013 = []
for x in mydata:
	releasedate = (mydata[x]['Release Year'])
	year = releasedate.split('-')[0]
	if year == '2013':
		length = mydata[x]['TrackLength']
		_2013.append(length)

_2014 = []
for x in mydata:
	releasedate = (mydata[x]['Release Year'])
	year = releasedate.split('-')[0]
	if year == '2014':
		length = mydata[x]['TrackLength']
		_2014.append(length)

_2015 = []
for x in mydata:
	releasedate = (mydata[x]['Release Year'])
	year = releasedate.split('-')[0]
	if year == '2015':
		length = mydata[x]['TrackLength']
		_2015.append(length)

_2016 = []
for x in mydata:
	releasedate = (mydata[x]['Release Year'])
	year = releasedate.split('-')[0]
	if year == '2016':
		length = mydata[x]['TrackLength']
		_2016.append(length)

_2017 = []
for x in mydata:
	releasedate = (mydata[x]['Release Year'])
	year = releasedate.split('-')[0]
	if year == '2017':
		length = mydata[x]['TrackLength']
		_2017.append(length)

avg2009 = round((sum(_2009) / len(_2009)),2)			#finding average track length per year
avg2010 = round((sum(_2010) / len(_2010)),2)
avg2011 = round((sum(_2011) / len(_2011)),2)
avg2013 = round((sum(_2013) / len(_2013)),2)
avg2014 = round((sum(_2014) / len(_2014)),2)
avg2015 = round((sum(_2015) / len(_2015)),2)
avg2016 = round((sum(_2016) / len(_2016)),2)
avg2017 = round((sum(_2017) / len(_2017)),2)

all_averages = [avg2009,avg2010,avg2011,avg2013,avg2014,avg2015,avg2016,avg2017]
years = ["2009","2011","2012","2013","2014","2015","2016","2017"]

#uncomment for below visualization, should open in plotly on your computer (offline plot.ly)

# plotly.offline.plot({
# 	"data": [Scatter(x= years , y= all_averages)],
# 	"layout": Layout(title = 'Average Song In Seconds Length by Year',
# 					xaxis = dict(title='Year'),
# 					yaxis = dict(title = 'Average Song Length (Seconds)', range = [200,300]))})


#										PART 4, INSTAGRAM

access_token = '185479668.5205ea7.604c2c4c5a5e41b1b461963fb63913b0'

Insta_Cache = "Insta_cache.json"
try:
    Insta_file = open(Insta_Cache, 'r')			#setting up cache
    Insta_contents = Insta_file.read()
    Insta_file.close()
    Insta_Diction = json.loads(Insta_contents)
except:
    Insta_Diction = {}


def Insta():
	if (len(Insta_Diction['Instagram']['data'])) == 20:		#if there is data for past 20 photos, use the cache
		print ('Insta Cached!')
		return (Insta_Diction)

	else:
		print ('Requesting Insta')
		x = requests.get('https://api.instagram.com/v1/users/self/media/recent/?access_token=' + access_token)
		
		Instadata = x.json()

		try:
			Insta_Diction['Instagram'] = Instadata    
			Instadump = json.dumps(Insta_Diction)
			fw = open(Insta_Cache, 'w')
			fw.write(Instadump)
			return (Instadump)
			fw.close()

		except:
			return ('Problem Caching')


x = Insta()

instadata = {}
	
for post in x['Instagram']['data']:					#making dictionary with all of the data I want from Insta API
	instadata[post['id']] = {
	'Caption_Length' : len(post['caption']['text']),
	'Likes' : post['likes']['count'],
	'Comments' : post['comments']['count'],
	'Tags' : len(post['tags']),
	'Other_Users' : len(post['users_in_photo'])}		#get a lot of things so I collect 100 data points  (5 points x 20 posts)

lot = [] #list of tuples for CTU + Traff v

for x in instadata:
	CTU = (instadata[x]['Caption_Length']) + (3 * instadata[x]['Tags']) + (3 * instadata[x]['Other_Users'])	# comments + hastags + users tagged (hastags + users tagged carry more weight b/c more eyes)
	traff = (instadata[x]['Likes']) + (5 * instadata[x]['Comments'])     # traffic on the post = likes + 5 * comments, comments mean people care more
	tup = (CTU,traff)
	lot.append(tup)		

conn = sqlite3.connect('Instagram.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Insta_Data')

cur.execute('''CREATE TABLE Insta_Data (ID TEXT, caption_length INTEGER, like_count INTEGER, comment_count INTEGER, tag_count INTEGER, other_users_count INTEGER)''')

for x in instadata:
	cur.execute("INSERT OR IGNORE INTO Insta_Data (ID, caption_length, like_count, comment_count, tag_count, other_users_count) VALUES (?, ?, ?, ?, ?, ?)",
		(x, (instadata[x]['Caption_Length']), (instadata[x]['Likes']),(instadata[x]['Comments']),(instadata[x]['Tags']), (instadata[x]['Other_Users'])))
		#store post id, caption length, like count, comment count, hashtags, and users tagged

conn.commit()

lot = sorted(lot, key = lambda x : x[0])

captagusers = []
traffic = []

for x in lot:
	captagusers.append(x[0])
	traffic.append(x[1])

#uncomment for below visualization, should open in plotly on your computer (offline plot.ly)

plotly.offline.plot({
	"data": [Scatter(x= captagusers , y= traffic, mode = 'markers')],
	"layout": Layout(title = 'Correlation Between Caption Length and Traffic on Instagram',
					xaxis = dict(title='Caption Length', range = [0,160]),
					yaxis = dict(title = 'Traffic', range = [150,340]))})



