import requests
import smtplib
from pymongo import MongoClient
from pprint import pprint
# API key
api_file=open("apikey.txt")
api_key=api_file.read()
api_file.close()

client= MongoClient("mongodb+srv://smritidas:justkidding@cluster0.jd128.mongodb.net")   
db=client.myCanvassingdb
available_i_curr_loc={}
for doc in db.Available_investigators.find():
	available_i_curr_loc[doc.get('id')]=doc.get('details')
location=input("enter the location to go:")
url="https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&"
dist={}
for key in available_i_curr_loc:
	if key!=None:
		print(key)
		r = requests.get(url+"origins=" + available_i_curr_loc[key]['curr_loc'] + "&destinations="+location + "&key=" +api_key)
		dist[key]=r.json()["rows"][0]["elements"][0]["duration"]["value"]
print(dist)