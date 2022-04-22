import re
from pymongo import MongoClient
from pprint import pprint
import requests
import smtplib
import datetime
from time import gmtime, strftime, localtime
import time
import sys

class Canvasser:
	def __init__(self, location,lang, sp):
		try:
			self.client= MongoClient("mongodb+srv://user:password@cluster0.jd128.mongodb.net")   
			self.db=self.client.myCanvassingdb
		except:
			print("OS error /network error, not able to connect to Mongodb please check credentials and Network access")
			return None
		
		try:
			self.url="https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&"
			self.api_file=open("apikey.txt")
			self.api_key=self.api_file.read()
			self.api_file.close()
		except:
			print("check if the api key text file is available in the same folder for google api access")
			return None
		self.location = location
		self.language = lang
		self.sp = sp.lower()
		self.location_check()
		
	def location_check(self):
		#check if location is underinvestigation. If not then allocate agents
		investigation_in_progress = []
		for doc in self.db.investigation_assigned.find():
			investigation_in_progress.append(doc.get('location'))
		
		if self.location in investigation_in_progress:
			print("location is already under investigation")
		else:
			a = self.allocate(self.sp)
			print(a)

	def allocate(self, sp):
	    	#get available investigators' details from database
		self.available_i_details={}
		for doc in self.db.Available_investigators.find():
			self.available_i_details[doc.get('id')]=doc.get('details')
			
		#get on-field investigators' details from database
		unavail_i_details={}
		for doc in self.db.Unavailable_investigators.find():
			unavail_i_details[doc.get('id')]=doc.get('details')
			
		inv_in_progress=[]
		dist={}
		eta={}
		alloted_i=[]
		
		#calculate ETA for available and not available investigators
		dist= self.ETA(self.available_i_details, "available")
		print(dist)
		eta=self.ETA(unavail_i_details, "unavailable")
		print(eta)
		
	    	#Here I am sorting the distance from nearest to farthest investigator. Using 2 lists for available and unavailble lists

		dist=dict(sorted(dist.items() , key=lambda item:item[1]))
		eta=dict(sorted(eta.items() , key=lambda item:item[1]))
	    
		#storing the ETA, only distance, for available and not available investigators in different lists
		list_dist=list(dist.values())
		list_eta=list(eta.values())
		# storing the keys based on ascending ETA
		keys_list_dist=list(dist)
		keys_list_eta=list(eta)
		# getting all investigators' details from db
		investigator_details={}
		for doc in self.db.All_inv.find():
			if doc.get('id') in keys_list_dist:
				investigator_details[doc.get('id')] = doc.get('details')
		# checking 
		if sp!= "no":
			if sp=="cryptanalyst" or sp.upper()=="IT" or sp=="forensic chemist" or sp=="connoisseur":
				alloted_i=self.special_assignment(keys_list_dist, keys_list_eta, list_dist, list_eta, dist, eta, alloted_i,sp)
				self.db.investigation_assigned.insert_one({"location":self.location, "investigators":alloted_i})
				return alloted_i
			else:
				print("None of the specializations match enter correct one")
				return None

		#if the available list of investigators is empty then assign the 2 investigators from unavailable list who are closest. 	
		if len(list_dist)==0:
			alloted_i.append(keys_list_eta[0])
			alloted_i.append(keys_list_eta[1])
			return alloted_i
		#check if the two or one from unavailable list are closer than agents from available list. If so, assign accordingly.
		else:
			if list_dist[0]>(list_eta[0]) :
				alloted_i.append(keys_list_eta[0])
				if list_dist[0]>(list_eta[1]): 
					alloted_i.append(keys_list_eta[1])
					print("following officers are nearby, contact them:")
					self.db.investigation_assigned.insert_one({"location":self.location,"investigators":alloted_i})
					return alloted_i
		
		for k in dist:
			if self.location in investigator_details[k]["knows_loc"]:
				alloted_i.append(k)
				self.available_to_unavailable(key)
				del self.available_i_details[k]

			if len(alloted_i)==2:             
				print(alloted_i)
				self.db.investigation_assigned.insert_one({"location":location, "investigators":alloted_i})
				print("returning in knows_loc")
				return alloted_i

		for key in self.available_i_details:
			if key!=None and investigator_details[key]["fluent_in"]==self.language:
				alloted_i.append(k)
				self.available_to_unavailable( key)
			if len(alloted_i)==2:
				print (alloted_i)
				self.db.investigation_assigned.insert_one({"location":location,"investigators":alloted_i})
				print("returning in fluent_in")
				return alloted_i

		for i in alloted_i:
			self.available_i_details.pop(i, None)

		for key in dist:
			
			if key != None and key not in alloted_i and len(alloted_i)<2:
				alloted_i.append(key)
				self.available_to_unavailable(key)
				del self.available_i_details[key]
				
			if len(alloted_i)==2:
				print (alloted_i)
				self.db.investigation_assigned.insert_one({"location":self.location, "investigators":alloted_i})
				print("returning avai based on dist")
				return alloted_i
	def available_to_unavailable(self, key):
		deets={}
		deets[key]=self.available_i_details[key]
		deets[key]['assignment_time'] = time.strftime("%H:%M:%S", localtime())
		deets[key]['start_time'] = ""
		self.db.Unavailable_investigators.insert_one({"id":key,"details":deets[key]})
		self.db.Available_investigators.delete_one({"id":key})
		
	def specialization(self, sp):
		arr=[]
		for doc in self.db.Specialization.find():
			print(doc.get('sp').lower())
			if doc.get('sp').lower()==sp:
				return doc.get('id')
			
	def special_assignment(self, keys_list_dist, keys_list_eta, list_dist, list_eta, dist, eta, alloted_i,sp):
		arr=[]
		count=-1
		count_d=-1
		count_e=-1
		arr = self.specialization(sp)
		print("arr:", arr)
		for k in arr:
			
			if (k in set(dist.keys())) and count_d==-1:
				print("inside if")
				val_d = dist[k]
				print("val_d:", val_d)
				count_d = list(dist.keys()).index(k)
				print("count_d:", count_d)
						
			elif (k in set(eta.keys())) and count_e==-1:
				print("inside if eta")
				val_e = eta[k]
				print("val_e:", val_e)
				count_e = list(eta.keys()).index(k)
				print("count_e:", count_e)
				
			if  count_e > 0 and count_d > 0:
				if val_e <= val_d:
					alloted_i.append(keys_list_eta[count_e])
					prev = count_e - 1
					next = count_e + 1
					if abs(list_eta[prev]- val_e) > abs(list_eta[next]- val_e):
						alloted_i.append(keys_list_eta[next])		
					else:
						alloted_i.append(keys_list_eta[prev])
					print("return 1:", alloted_i)
					
					return alloted_i
				elif val_d < val_e:
					alloted_i.append(keys_list_dist[count_d])
					self.available_to_unavailable(keys_list_dist[count_d])
					prev = count_d - 1
					next = count_d + 1
					if (abs(list_dist[prev]- val_d) > abs(list_dist[next]- val_d)):
						alloted_i.append(keys_list_dist[next])		
						self.available_to_unavailable(keys_list_dist[next])
					else:
						alloted_i.append(keys_list_dist[prev])
						self.available_to_unavailable(keys_list_dist[prev])
					print("return 2:", alloted_i)
					return alloted_i
		if count_e > 0 and count_d==0:
			if val_e > val_d:
				alloted_i.append(keys_list_dist[count_d])
				self.available_to_unavailable(keys_list_dist[count_d])
				if list_eta[count_e-1] < list_dist[count_d+1]:
					alloted_i.append(keys_list_eta[coun_e-1])
					
				else:
					alloted_i.append(keys_list_dist[count_d+1])
					self.available_to_unavailable(keys_list_dist[count_d+1])
				print("return 3:", alloted_i)
				return alloted_i
			elif val_d > val_e:
				alloted_i.append(keys_list_eta[count_e])
				
				alloted_i.append(keys_list_eta[count_e-1])
				
				print("return 4:", alloted_i)
				return alloted_i
					
		elif count_d > 0 and count_e==0:
			if val_d > val_e:
				alloted_i.append(keys_list_eta[count_e])
				
				if list_dist[count_d-1] < list_eta[count_e+1]:
					alloted_i.append(keys_list_dist[coun_d-1])
					self.available_to_unavailable(keys_list_dist[count_d-1])
				else:
					alloted_i.append(keys_list_eta[count_e+1])
				print("return 5:", alloted_i)
				return alloted_i
			elif val_e > val_d:
				alloted_i.append(keys_list_dist[count_d])
				self.available_to_unavailable(keys_list_dist[count_d])
				alloted_i.append(keys_list_dist[count_d-1])
				self.available_to_unavailable(keys_list_dist[count_d-1])
				print("return 6:", alloted_i)
				return alloted_i
		elif count_d==0 and count_e==0:
			if val_e < val_d:
				alloted_i.append(keys_list_eta[count_e])
				
				if list_eta[count_e+1] > val_d:
					alloted_i.append(keys_list_dist[count_d])
					self.available_to_unavailable(keys_list_dist[count_d])
				else:
					alloted_i.append(keys_list_eta[count_e+1])
				print("return 7:", alloted_i)
				return alloted_i
			elif val_d < val_e:
				alloted_i.append(keys_list_dist[count_d])
				self.available_to_unavailable(keys_list_dist[count_d])
				if list_dist[count_d+1] > val_e:
					alloted_i.append(keys_list_eta[count_e])
				else:
					alloted_i.append(keys_list_dist[count_d+1])
					self.available_to_unavailable(keys_list_dist[count_d+1])
				print("return 8:", alloted_i)
				return alloted_i
		elif count_e==-1:
			alloted_i.append(keys_list_dist[count_d])
			self.available_to_unavailable(keys_list_dist[count_d])
			alloted_i.append(keys_list_dist[count_d+1])
			self.available_to_unavailable(keys_list_dist[count_d+1])
			print("return 9:", alloted_i)
			return alloted_i
		elif count_d==-1:
			alloted_i.append(keys_list_eta[count_e])
			alloted_i.append(keys_list_eta[count_e+1])
			print("return 10:", alloted_i)
			return alloted_i
		

	def ETA(self,i_details, option):
		dist={}
		for key in i_details:
			if key!=None:
				r = requests.get(self.url+"origins=" + i_details[key]['curr_loc'] + "&destinations="+self.location + "&key=" +self.api_key)
				if option == 'unavailable':
					
					now=time.strftime("%H:%M:%S", localtime())
					start_time = time.strptime(i_details[key]['start_time'],'%H:%M:%S')
					now_time = time.strptime(now,'%H:%M:%S')
					print("time difference:", (time.mktime(now_time)-time.mktime(start_time))/60)
					dist[key]=r.json()["rows"][0]["elements"][0]["duration"]["value"] + (20 - (time.mktime(now_time)-time.mktime(start_time))/60)
					
				elif option == 'available':
					dist[key]=r.json()["rows"][0]["elements"][0]["duration"]["value"] 					
				print(r.json()["rows"][0]["elements"][0]["duration"]["text"])
		print("calculated time:", dist)
		return dist

if __name__=='__main__':
	c = Canvasser(sys.argv[1], sys.argv[2], sys.argv[3])
	



