# Algo_S22
algo for assigning investigators to location

The first step is to import the available investigator list from DB and create an unordered map/ dictionary with Key as ID of the investigator and value as the dictionary of values {Name, current location, fluent in languages, Knowledge about area}. Right now the knowledge about area is a "Yes" or "No field". It will be better to save the street/ avenue name instead, which will convey the avenues the investigator has knowledge about.(If an investigator goes to a new avenue for investigation, adding that avenue to known will be useful for future assignments)
The investigators will keep their locations updated (reflected in database column for current location) which will be used to calculate the time to reach the destination (ETA is given by one of the maps APIs). This will be saved in dist variable which is used to figure out the closest investigator to the destination location.
The first preference is given to the familiarity of investigator to a location. Next is the distance/time it will take to reach the destination. Other parameters will be added in the later stages of project.  
