import re
from pymongo import MongoClient
from pprint import pprint
import requests
import smtplib
import datetime
from time import gmtime, strftime
import time
import sys

class Canvasser:
	def __init__(self, location,lang):
		self.url="https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&"
		self.client= MongoClient("mongodb+srv://username:password@cluster0.jd128.mongodb.net")   
		self.db=self.client.myCanvassingdb
		self.location= location
		self.language= lang
		self.location_check()
		
	def location_check(self):
	
		investigation_in_progress = []
		for doc in self.db.investigation_assigned.find():
			investigation_in_progress.append(doc.get('location'))
		
		if self.location in investigation_in_progress:
			print("location is already under investigation")
		else:
			a = self.allocate()
			print(a);
			
	'''def add_to_available_list(self):'''

	def allocate(self):
	    
		available_i_details={}
		for doc in self.db.Available_investigators.find():
			available_i_details[doc.get('id')]=doc.get('details')
			

		unavail_i_details={}
		for doc in self.db.Unavailable_investigators.find():
			unavail_i_details[doc.get('id')]=doc.get('details')
			
		inv_in_progress=[]
	    
		dist={}
		eta={}
		alloted_i=[]
		'''storing the distances. Later I will try to use ETA from maps instead. Right now I have used the distances of avenues as distance'''	
		
		dist= self.ETA(self.url, self.location, available_i_details, "available")
		print(dist)
		eta=self.ETA(self.url, self.location, unavail_i_details, "unavailable")
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
		investigator_details={}
		for doc in self.db.All_inv.find():
			if doc.get('id') in keys_list_dist:
				investigator_details[doc.get('id')] = doc.get('details')
		
		
		if len(list_dist)==0:
			alloted_i.append(keys_list_eta[0])
			alloted_i.append(keys_list_eta[1])
			return alloted_i
		else:
			
			if list_dist[0]>(list_eta[0]) :
				alloted_i.append(keys_list_eta[0])
				if list_dist[0]>(list_eta[1]): 
					alloted_i.append(keys_list_eta[1])
					print("following officers are nearby, contact them:")
					self.db.investigation_assigned.insert_one({"location":location,"investigators":alloted_i})
					return alloted_i
		
		for k in dist:
			if self.location in investigator_details[k]["knows_loc"]:
				alloted_i.append(k)
				self.db.Unavailable_investigators.insert_one({"id":k,"details":available_i_details[k]})
				self.db.Available_investigators.delete_one({"id":k})
				del available_i_details[k]

			if len(alloted_i)==2:             
				''' If I already found the required number of investigators, here 2, I will return without further processing'''
				print(alloted_i)
				self.db.investigation_assigned.insert_one({"location":location, "investigators":alloted_i})
				return alloted_i

		'''If I haven't found the required # investigators I will look for an investigator who doesn't know about the area but speaks the language that the household(location) speaks'''
		for key in available_i_details:
			if key!=None and investigator_details[key]["fluent_in"]==self.language:
				alloted_i.append(k)
				self.db.Unavailable_investigators.insert_one({"id":key,"details":available_i_details[key]})
				self.db.Available_investigators.delete_one({"id":key})
			if len(alloted_i)==2:
				print (alloted_i)
				self.db.investigation_assigned.insert_one({"location":location,"investigators":alloted_i})
				return alloted_i
		''' Since the previous iteration was on available_i_details I did not remove the investigators from list, which is what I an doing here'''
		for i in alloted_i:
			available_i_details.pop(i, None)

		''' Here I am just assigning officers based on their vicinity to the location'''
		for key in dist:
			deets={}
			if key != None and key not in alloted_i and len(alloted_i)<2:
				alloted_i.append(key)
				deets[key]=available_i_details[key]
				deets[key]['start_time'] = time.strftime("%H:%M:%S", gmtime())
				self.db.Unavailable_investigators.insert_one({"id":key,"details":available_i_details[key]})
				self.db.Available_investigators.delete_one({"id":key})
				del available_i_details[key]
			if len(alloted_i)==2:
				print (alloted_i)
				self.db.investigation_assigned.insert_one({"location":self.location, "investigators":alloted_i})
				return alloted_i

	def ETA(self, url,location, i_details, option):

		api_file=open("apikey.txt")
		api_key=api_file.read()
		api_file.close()
		
		dist={}
		for key in i_details:
			if key!=None:
				r = requests.get(url+"origins=" + i_details[key]['curr_loc'] + "&destinations="+location + "&key=" +api_key)
				if option == 'unavailable':
					
					now=time.strftime("%H:%M:%S", gmtime())
					start_time = time.strptime(i_details[key]['start_time'],'%H:%M:%S')
					now_time = time.strptime(now,'%H:%M:%S')
					print("time difference:", (time.mktime(now_time)-time.mktime(start_time))/60)
					
					dist[key]=r.json()["rows"][0]["elements"][0]["duration"]["value"] + (900 - (time.mktime(now_time)-time.mktime(start_time))/60)
					
				elif option == 'available':
					dist[key]=r.json()["rows"][0]["elements"][0]["duration"]["value"] 					
				print(r.json()["rows"][0]["elements"][0]["duration"]["text"])
		print("calculated time:", dist)
		return dist

if __name__=='__main__':
	c = Canvasser(sys.argv[1], sys.argv[2])
	
