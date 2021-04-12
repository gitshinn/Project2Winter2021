#################################
##### Name: Kristian Shin
##### Uniqname: shinkris
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import re

#importing the API keys
client_key = secrets.MAPQUEST_API_KEY
client_secret = secrets.MAPQUEST_API_SECRET

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    #defining the function based on the described parameters
    def __init__(self, category="No Category", name="No Name", address="No Address", zipcode="No Zip-Code", phone = "No Phone Number"):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    #prints national site based on state in the desired format
    def info(self):
        return self.name + " (" + self.category + "): " + self.address + " " + self.zipcode

#cache dictionary created for storage and easy recall
CACHE_DICT = {}

def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    ###using response and soup to parse the page for state list elements
    url = 'https://www.nps.gov/index.htm'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    state_list_elements = soup.find_all(href = re.compile("state"))

    #making dictionary that maps state name to state page url
    state_url_dict = {}
    base_url = "https://www.nps.gov"
    for list_element in state_list_elements:
        current_url = list_element["href"]
        full_url = base_url + current_url
        state_url_dict[list_element.string.lower()] = full_url
    return(state_url_dict)


def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    #checking cache for parameter
    if site_url in CACHE_DICT:
        print("Using Cache")
        return CACHE_DICT[site_url]
    #if not in cache, use soup to parse the page for the name, category, zip, address, and phone of the input
    #then save it to a cache for future reference
    else:
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        name = soup.find(class_="Hero-title").string.strip()
        category = soup.find(class_="Hero-designation")
        if category is None or category.string is None:
            category = "None"
        else:
            category = category.string.strip()
        zip = soup.find(class_="postal-code").string.strip()
        address = soup.find(itemprop="addressLocality").string + ", " + soup.find(class_="region").string
        phone = soup.find(class_="tel").string.strip()
        site = NationalSite(category, name, address, zip, phone)
        CACHE_DICT[site_url.lower()] = site
        print("Fetching")
        return site


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    #calling the inputted url then parsing the page with BeautifulSoup
    response = requests.get(state_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    parks_in_state = soup.find(id = "list_parks").find_all("h3")

    #looping over the parks in state to get the urls and put them in a new list
    state_url_list = []
    base_url = "https://www.nps.gov"
    for park in parks_in_state:
        current_url = park.a["href"]
        state_url_list.append(base_url + current_url)

    #loop over the list of urls to make a list of site instances calling get_site_instance()
    list_of_site_instances = []
    for url in state_url_list:
        list_of_site_instances.append(get_site_instance(url))
    #print(list_of_site_instances)
    return(list_of_site_instances)


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    #if parameter is in cache, access it
    if site_object.zipcode in CACHE_DICT:
        print("Using Cache")
        return CACHE_DICT[site_object.zipcode]
    #if parameter is not in cache, access the mapquest api
    #then save the result (a dictionary from the json) to the CACHE DICTIONARY
    else:
        print("Fetching")
        params = {"key": client_key, "origin": site_object.zipcode, "radius": 10, "units": "m", "maxMatches": 10, "ambiguities": "ignore", "outFormat": "json"}
        mapquest_response = requests.get("http://www.mapquestapi.com/search/v2/radius", params)
        #saving the text of mapquest_response
        json_str = mapquest_response.text
        #Making a dictionary object from the json
        mapquest_result = json.loads(json_str)
        CACHE_DICT[site_object.zipcode] = mapquest_result
        return mapquest_result


###MAIN FUNCTION
if __name__ == "__main__":
    ###user prompted to enter a search term or exit
    user_input = input('Enter a state name (e.g. Michigan, michigan), or "exit" to quit:').lower()
    #make a dictionary of state names to abbreviations
    state_url_dict = build_state_url_dict()
    #keep repeating function until user types exit
    while user_input != "exit":
        #check if user_input is actually a state
        if user_input in state_url_dict:
            state_url = state_url_dict[user_input]
            sites_for_state = get_sites_for_state(state_url)
            #header for list of national sites
            print("-----------------------------------------")
            print("List of national sites in " + user_input)
            print("-----------------------------------------")
            #Adding a counter to add to the beginning of each item in the list
            ct = 1
            for site in sites_for_state:
                print("[" + str(ct) + "] " + site.info())
                ct += 1
            #second input to check for nearby sites
            detail_input = input(' Choose the number for detail search or "exit" or "back" ')
            while detail_input:
                if detail_input == "back":
                    break
                if detail_input == "exit":
                    quit()
                elif not detail_input.isdigit() or int(detail_input) > len(sites_for_state) or int(detail_input) <= 0:
                    print("[Error] Invalid input")
                else:
                    #use get_nearby_places to check mapquest
                    mapquest_result = get_nearby_places(sites_for_state[int(detail_input)-1])
                    #header
                    print("-----------------------------------------")
                    print("Places near " + sites_for_state[int(detail_input)-1].name)
                    print("-----------------------------------------")
                    #loop to check for null categories then print desired string for each nearby place
                    for place in mapquest_result['searchResults']:
                        if not place['fields']['group_sic_code_name']:
                            place['fields']['group_sic_code_name'] = "No Category"
                        if not place['fields']['address']:
                            place['fields']['address'] = "No Address"
                        if not place['fields']['city']:
                            place['fields']['city'] = "No City"
                        print('<' + place['name'] + '> ' +"(<" + place['fields']['group_sic_code_name'] + ">): " + "<" + place['fields']['address'] + ">," + "<" + place['fields']['city'] + ">")
                detail_input = input(' Choose the number for detail search or "exit" or "back" ')
        else:
            print("[Error] Enter proper state name")
        user_input = input('Enter a state name (e.g. Michigan, michigan), or "exit" to quit:').lower()

