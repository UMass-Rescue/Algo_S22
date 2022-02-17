import re

def allocate(location="48th Av, Block 10, House 4", lang="Spanish"):
    
    '''this is just for testing purpose. Next week I will use MongoDB to fetch tables and update tables. Using the information from tables available_investigator_details dictioinary will be updated'''

    available_i_details={1234: {"Name":"Jagath","knows_loc":"No", "fluent_in":["English", "Spanish"], "curr_loc":"56th Av"},2345:{"Name":"Ben", "knows_loc":"No", "fluent_in":["English","Greek"],"curr_loc":"48th Av"},3456:{"Name":"Sam","knows_loc":"No","fluent_in":["English","French"],"curr_loc":"51st Av"},7892:{"Name":"Colette", "knows_loc":"No","fluent_in":["English"],"curr_loc":"49th Av"},4536:{"Name":"Smriti", "knows_loc":"No", "fluent_in":["English","Hindi"],"curr_loc":"45th Av"}}
    


    unavail_i_detail={} '''this variable is for next update. Not used now'''
    
    inv_in_progress=[]  ''' to save the locations of ongoing interviews. This will later be updated in a db table'''

    ''' Here I am just cleaning the location. In the upcoming updates I will fetch location from map for the investigator's curr_location and the interview location will be entered by the coordinator. '''

    loc_split=location.split(' ')
    Avenue=re.sub("[^0-9]","",loc_split[0])
    Block=loc_split[1]
    House=loc_split[2]
    
    inv_in_progress.append(location)

    ''' dist is for storing the distances of each available investigator from the location to be assigned
        alloted_i is used to store the IDs of investigators assigned to this particular location
    '''

    dist={}
    alloted_i=[]

    '''storing the distances. Later I will try to use ETA from maps instead. Right now I have used the distances of avenues as distance'''

    for key in available_i_details:
        d=re.sub("[^0-9]","",available_i_details[key]['curr_loc'])
        dist[key]=abs(int(d)-int(Avenue))


    '''Here I am sorting the distance from nearest to farthest investigator'''

    dict(sorted(dist.items() , key=lambda item:item[1]))

    '''First priority is given to knows_loc, which has the details if the investigator is familiar with the area of assignment. If he/she/they are then the investigator is assigned to the location in question and is removed from the available list of investigators. I have used sorted dist for iterating so that while assignment of investigators, nearest investigator whoc knows about the area is assigned'''
    for k in dist:
        if available_i_details[k]["knows_loc"]=="Yes":
            alloted_i.append(k)
            del available_i_details[k]

        if len(alloted_i)==2:              ''' If I already found the required number of investigators, here 2, I will return without further processing'''
            print(alloted_i)
            return alloted_i

'''If I haven't found the required # investigators I will look for an investigator who doesn't know about the area but speaks the language that the household(location) speaks'''

    for key in available_i_details:
        if available_i_details[key]["fluent_in"]==lang:
            alloted_i.append(k)

        if len(alloted_i)==2:
            print (alloted_i)
            return alloted_i
    
    for i in alloted_i: ''' Since the previous iteration was on available_i_details I did not remove the investigators from list, which is what I an doing here'''
        available_i_details.pop(i, None)

''' Here I am just assigning officers based on their vicinity to the location'''
    for key in dist:
        if key not in alloted_i and len(alloted_i)<2:
            alloted_i.append(key)
            del available_i_details[key]
        if len(alloted_i)==2:
            print (alloted_i)
            return alloted_i
    print("not enough investigators available. redirect request to the one closest to the location")
    
    return alloted_i



allocate("48th Av, Block 10, House 4", "Spanish")

