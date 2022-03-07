import re
from pymongo import MongoClient
from pprint import pprint
import requests
import smtplib
import sys

def allocate(location, lang):
    
	'''this is just for testing purpose. Next week I will use MongoDB to fetch tables and update tables. Using the information from tables available_investigator_details dictioinary will be updated'''
	client= MongoClient("mongodb+srv://smritidas:justkidding@cluster0.jd128.mongodb.net")   
	db=client.myCanvassingdb
	available_i_details={}
	for doc in db.Available_investigators.find():
		available_i_details[doc.get('id')]=doc.get('details')

	unavail_i_details={}
	for doc in db.Unavailable_investigators.find():
		unavail_i_details[doc.get('id')]=doc.get('details')
	inv_in_progress=[] 
	''' to save the locations of ongoing interviews. This will later be updated in a db table'''

	''' Here I am just cleaning the location. In the upcoming updates I will fetch location from map for the investigator's curr_location and the interview location will be entered by the coordinator. 
	dist is for storing the distances of each available investigator from the location to be assigned
        alloted_i is used to store the IDs of investigators assigned to this particular location
	'''
    
	dist={}
	eta={}
	alloted_i=[]
	'''storing the distances. Later I will try to use ETA from maps instead. Right now I have used the distances of avenues as distance'''	
	url="https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&"
	dist= ETA(url, location, available_i_details)
	print(dist)
	eta=ETA(url, location, unavail_i_details)
	print(eta)
	'''
    	Here I am sorting the distance from nearest to farthest investigator'''

	dist=dict(sorted(dist.items() , key=lambda item:item[1]))
	eta=dict(sorted(eta.items() , key=lambda item:item[1]))
    
	'''checking if there are two officers already out and nearby, from the unavailable list'''
	list_dist=list(dist.values())
	list_eta=list(eta.values())
	keys_list_dist=list(dist)
	keys_list_eta=list(eta)
	if list_dist[0]>(list_eta[0]+900) :
		alloted_i.append(keys_list_eta[0])
		if list_dist[0]>(list_eta[1]+900): 
			alloted_i.append(keys_list_eta[1])
			print("following officers are nearby, contact them:")
			db.investigation_assigned.insert_one({"location":location,"investigators":alloted_i})
			return alloted_i
	'''First priority is given to knows_loc, which has the details if the investigator is familiar with the area of assignment. If he/she/they are then the investigator is assigned to the location in question and is removed from the available list of investigators. I have used sorted dist for iterating so that while assignment of investigators, nearest investigator whoc knows about the area is assigned'''
	for k in dist:
		if available_i_details[k]["knows_loc"]=="Yes":
			alloted_i.append(k)
			db.Unavailable_investigators.insert_one({"id":k,"details":available_i_details[k]})
			db.Available_investigators.delete_one({"id":k})
			del available_i_details[k]

		if len(alloted_i)==2:             
			''' If I already found the required number of investigators, here 2, I will return without further processing'''
			print(alloted_i)
			db.investigation_assigned.insert_one({"location":location, "investigators":alloted_i})
			return alloted_i

	'''If I haven't found the required # investigators I will look for an investigator who doesn't know about the area but speaks the language that the household(location) speaks'''
	for key in available_i_details:
		if key!=None and available_i_details[key]["fluent_in"]==lang:
			alloted_i.append(k)
			db.Unavailable_investigators.insert_one({"id":key,"details":available_i_details[key]})
			db.Available_investigators.delete_one({"id":key})
		if len(alloted_i)==2:
			print (alloted_i)
			db.investigation_assigned.insert_one({"location":location,"investigators":alloted_i})
			return alloted_i
	''' Since the previous iteration was on available_i_details I did not remove the investigators from list, which is what I an doing here'''
	for i in alloted_i:
		available_i_details.pop(i, None)

	''' Here I am just assigning officers based on their vicinity to the location'''
	for key in dist:
		if key != None and key not in alloted_i and len(alloted_i)<2:
			alloted_i.append(key)
			db.Unavailable_investigators.insert_one({"id":key,"details":available_i_details[key]})
			db.Available_investigators.delete_one({"id":key})
			del available_i_details[key]
		if len(alloted_i)==2:
			print (alloted_i)
			db.investigation_assigned.insert_one({"location":location, "investigators":alloted_i})
			return alloted_i

def ETA(url,location, i_details):

	api_file=open("apikey.txt")
	api_key=api_file.read()
	api_file.close()

	dist={}
	for key in i_details:
		if key!=None:
			r = requests.get(url+"origins=" + i_details[key]['curr_loc'] + "&destinations="+location + "&key=" +api_key)
			dist[key]=r.json()["rows"][0]["elements"][0]["duration"]["value"]
			print(r.json()["rows"][0]["elements"][0]["duration"]["text"])
	return dist
if __name__=='__main__':
	allocate(sys.argv[1], sys.argv[2])

