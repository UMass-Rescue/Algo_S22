# Algo_S22
algo for assigning investigators to location

The first preference is given to the familiarity of investigator to a location. Next is the distance/time it will take to reach the destination. Other parameters will be added in the later stages of project.  

installations:
First to install mongoDB 
>>wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add - 

>>echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/5.0 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list 

>>sudo apt-get update

>>sudo apt-get install -y mongodb-org

For more details about mongoDB installation refer https://docs.mongodb.com/manual/tutorial/install-mongodb-on-debian/ (since I used debian based OS)

Next install pymongo (I did that using pip which was not installed in my machine so I have added steps for that as well)
>>sudo apt-get install pip 

>>sudo apt-get pip install --upgrade pip  

>>sudo apt update 

>>sudo apt install python3-pip  

>>pip3 --version             (to check version)

pip 22.0.2 from /usr/lib/python3/dist-packages/pip (python 3.9)                    (Versions I am using, including python version)

>>pip3 install pymongo 


To run the python file in CLI:

>>python3 canvasser.py "String-Address" "String-name of Language"
