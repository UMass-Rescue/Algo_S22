**MOTIVATION:**

The intent behind the algorithm is to make it easier for the coordinator to keep track of progress of an investigation, where the investigations need to be conducted and assign the agents to the interview locations in a way that it saves time, both the coordination time and interview/travel time.

Tech Stack includes:

Python3
Mongodb
Google Maps API

**WHAT I DID?**

INPUT: The algorithm takes input from the user. These inputs are Address/location where the agents should visit to investigate/interview and the Language the surrounding/household speaks. The next input is if there is a requirement of an agent who specializes in a certain field (this part is not integrated with the front end).

OUTPUT: The output is the two agents’ ids who have been assigned to visit the location entered by the coordinator. First I prioritize the specialization requirement. The selection of agents then revolves around the agents who specialize in that particular field as mentioned by the coordinator. Out of the agents who specialize in a field, whoever is closest is selected first and then the other agent is selected based on who can reach the location at nearly the same time as the first agent selected (the one who specializes).
If no specialization is required then the time required to reach that location is given first priority. The agents who take the least time to reach a location no matter what their current status is, If they are available or currently conducting the interviews. Then I check if the agent is familiar with the location. Finally, if the agent knows the language the household speaks.

DATABASE: In the database, there are multiple collections (I mention collections since I use Mongodb as the database). 
The first collection (All_Inv) has the details of all investigators. Corresponding to the IDs the details include familiarity with Areas, Languages they speak, Name, Cases and Designation. The other collection is of investigators who are available (available_investigators) which has fields ID and current location. 
The third is a list of unavailable investigators who will start to work or who are already on field. This collection has fields ID, current location and start time. Start time gets updated by default as the time right now plus the time it will take the investigators to reach the location and start which will be approximately the time they update from the mobile app that the interview has started. The fourth collection mentions the specializations and the investigators’ IDs who specialize in that field. The last collection is the investigation assigned which has locations with either ongoing investigations or already done with.

API: I used Google APIs to calculate the ETA for the investigators. I need an API key for that which is saved in the text file locally that the program accesses.

**HOW TO USE?**

There’s a desktop application for using the algorithm. The coordinator inputs the address/location in the address field and Language in the Language field. And the output will be received as the IDs of investigators who should be contacted to visit that location.

If running only the algorithm use
 >> python3 canvasser.py  “address/ location” “language”

Pass address and language as arguments. After this the prompt asks the question if specialized agents are required? And the options along with that. If the specialization is required then type which specialization otherwise type “No”. The specialization options given right now are of Cryptanalyst, IT, Forensic Chemist and Connoisseur. 
The output will be a list with IDs of two investigators.

**ADDITIONAL FEATURES:**

The algorithm I have written is a very basic skeleton which is based on a few assumptions such as the number of people working on a case are around 10-15 (which is ideal case though) such that the time complexity would not impact the performance much. Another assumption is that I/O works perfectly fine without network failure and security issues. So there is scope of improvement.

Currently I am considering that the coordinator is managing only one case, ‘GAMMA’. Although it may be the case that the coordinator manages multiple cases and a few special agents are working on multiple cases which will impact the availability. This can be implemented in future. Based on this I will need to add the field where first I select the Case name.

Asynchronous programming can be added to improve the response time.  Fault tolerance needs to be handled with replication (with or without Docker). Once there is replication Data inconsistency needs to be handled across databases and collections. (Need to check the implementation of locks while updating the db.)

Connecting the front-end with the part of the algorithm which updates the unavailable investigators to available investigators once the agent updates that he/she is done with their interviews on the mobile application. The approximation of start time can be improved.

Contacting the investigators directly without the coordinator intervening. 

Connecting the live location of the agents to the desktop application.

Thinking of ways to optimize the algorithm itself, using data structures to optimize time and space complexity.
Ways to improve the design of the database and integrating with the backend with postgres where all other sections of the projects are hosted (Interview Transcriber, License Plate Identifier, Dense Image Captioning).

Need to consider the security aspects carefully. Example, use of environment variables for mongodb credentials while dockerizing.

**Summary:**
I learnt alot from being a part of this project. Although I could not implement the front end by myself, I learnt in the process. An example of learning was Azure blob implementation. Even though I did not use it, just giving it a try and coming across errors helped me learn. The backend implementation was something I would have loved to do but due to time constraints that could not happen. Also, the improvement part I have mentioned I hoped to have implemented at least some of those. One of the most important lessons for me was the CI/CD (Sam’s presentation on CI/CD was well done) and other presentations also helped me learn new topics.

