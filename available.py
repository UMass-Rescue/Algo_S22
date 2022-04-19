
from pymongo import MongoClient
from pprint import pprint
import sys

class Change_Availability:
	def __init__(self, id_no):
		try:
			self.client= MongoClient("mongodb+srv://user:password@cluster0.jd128.mongodb.net")   
			self.db=self.client.myCanvassingdb
		except (OSError):
			print("OS error /network error, not able to connect to Mongodb please check credentials and Network access")
		self.unavailable_to_available(id_no)
		
	def unavailable_to_available(self, id_no):
		id_no=int(id_no)
		unavail_i_details={}
		for doc in self.db.Unavailable_investigators.find():
			unavail_i_details[doc.get('id')]=doc.get('details')
			if doc.get('id')==id_no:
				x=unavail_i_details[id_no].pop('start_time', None)
				if self.db.Available_investigators.count_documents( {'id': id_no} ) == 0:
					self.db.Available_investigators.insert_one({"id":id_no,"details":unavail_i_details[id_no]})	
				self.db.Unavailable_investigators.delete_one({"id":id_no})
				break
if __name__=='__main__':
	c=Change_Availability(sys.argv[1])
	
