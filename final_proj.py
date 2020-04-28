import secrets
import requests
import sqlite3
import json
from bs4 import BeautifulSoup

#SETTING UP PART
api_key = secrets.api_key
yelp_headers = {'Authorization': 'Bearer %s' % api_key}
yelp_search_url = 'https://api.yelp.com/v3/businesses/search'

headers = {
    'User-Agent': 'UMSI 507 Course Project - Python Scraping',
    'From': 'tianyuey@umich.edu', 
    'Course-Info': 'https://si.umich.edu/programs/courses/507'
}

CACHE_FNAME = 'cache.json'
CACHE_DICT = {}
cuisine_type = 'restaurants'
DB_NAME = 'site_restaurant.sqlite'

def load_cache():
    '''Take content from cache file, called only once when start running the program

    Parameters
    ----------
    None

    Returns
    -------
    dict
        the json object taken from cache file
    '''
    try:
        cache_file = open(CACHE_FNAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    '''Save new changes into cache file, called whenever the cache is changed

    Parameters
    ----------
    None

    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FNAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    '''Make webAPI requests using cache if retrieve data from existing cache file

    Parameters
    ----------
    url: string
        url to retrieve data from
    cache: dict
        existing cache dictionary to check content within

    Returns
    -------
    dict
        result dictionary got from making requests and checking cache file
    '''
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        response = requests.get(url, headers=headers)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

# def make_yelp_request_using_cache(search_params, cache):
#     '''Make webAPI requests using cache if retrieve data from existing cache file

#     Parameters
#     ----------
#     search_params: dict
#         search parameters to retrieve data from
#     cache: dict
#         existing cache dictionary to check content within

#     Returns
#     -------
#     dict
#         result dictionary got from making requests and checking cache file
#     '''
#     location = search_params['location']
#     if (location in cache.keys()): # the url is our unique key
#         print("Using cache")
#         return cache[location]
#     else:
#         print("Fetching")
#         response = requests.get(yelp_search_url, params=search_params, headers=yelp_headers)
#         cache[location] = response.text
#         save_cache(cache)
#         return cache[location]


def init_db_table():
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
    except:
        print("Sorry, fail to connect to the database.")

    #Check if tables already exist. Drop tables if they do.
    statement = '''
        DROP TABLE IF EXISTS 'Sites';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        DROP TABLE IF EXISTS 'Restaurants';
    '''
    cur.execute(statement)
    conn.commit()

    #Create tables
    statement = '''
        CREATE TABLE 'Sites' (
            "SiteId"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	        "SiteName"	TEXT NOT NULL,
	        "Street"	TEXT,
	        "City"	TEXT NOT NULL,
	        "RegionZip"	TEXT NOT NULL
        );
    '''
    try:
        cur.execute(statement)
    except:
        print("Fail to create table Sites.")
    conn.commit()

    statement = '''
        CREATE TABLE "Restaurants" (
	        "RestaurantId"	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	        "RestaurantName"	TEXT NOT NULL,
	        "CloseStatus"	TEXT NOT NULL,
	        "ReviewCount"	INTEGER NOT NULL,
	        "Category"	TEXT NOT NULL,
	        "Rating"	INTEGER NOT NULL,
	        "Price"	TEXT NOT NULL,
	        "Address1"	TEXT,
	        "Address2"	TEXT,
	        "Address3"	TEXT,
	        "City"	TEXT NOT NULL,
	        "ZipCode"	TEXT NOT NULL,
	        "State"	TEXT NOT NULL,
	        "Phone"	TEXT,
	        "SiteId"	INTEGER NOT NULL,
	        FOREIGN KEY("SiteId") REFERENCES "Sites"
        );
    '''
    try:
        cur.execute(statement)
    except:
        print("Fail to create table Restaurants.")
    conn.commit()

    #close db connection
    conn.close()


#Creating database implementation, called only once
#init_db_table() 

#SETTING UP ATTRACTIONS SITES DATA AND YELP DATA
CACHE_DICT = load_cache()
states = ['california', 'florida', 'nevada', 'texas']
sites_base_url = 'https://www.attractionsofamerica.com/attractions/'
sites_list = []
sites_location_list = []
state_sites_dict = {'california':'', 'florida':'', 'nevada':'', 'texas':''}
for state in states:
    site_url = sites_base_url + state + '.php'
    site_response = make_url_request_using_cache(site_url, CACHE_DICT)
    soup = BeautifulSoup(site_response, 'html.parser')

    sites_list_for_state = []
    sites_location_containers = soup.find_all('div', class_='box_style_1')
    for c in sites_location_containers:
        site_dict = {}
        site_parent = c.find('div', class_='pl10 pr10 pb10')
        if site_parent != None:
            site_name = site_parent.find('h2').text.split(': ')[1]
            site_dict['site_name'] = site_name
        location_source = c.find('p', class_='pl10 pr10 inner-titles-post')
        if location_source != None:
            get_location = location_source.text.split(' ')[1:]
            site_location = ' '.join(get_location)
            sites_location_list.append(site_location)
            site_dict['region_zip'] = site_location.split(', ')[-1].strip()
            site_dict['city'] = site_location.split(', ')[-2].strip()
            if len(site_location.split(', ')) >= 3:
                site_dict['street'] = site_location.split(', ')[-3].strip()
            else:
                site_dict['street'] = 'No street data'

        sites_list.append(site_dict)
        sites_list_for_state.append(site_dict)
        for site in sites_list_for_state:
            if site == {}:
                sites_list_for_state.remove(site)
    state_sites_dict[state] = sites_list_for_state
#print(state_sites_dict)
#print(sites_list)


location_dict_list = []
for location in sites_location_list:
    site_location_dict = {}
    site_location_dict['location'] = location
    site_location_dict['site_id'] = sites_location_list.index(location)+1
    location_dict_list.append(site_location_dict)

#print(location_dict_list)

#GETTING DATA FROM YELP
def search_on_yelp():
    '''TODO
    '''
    cuisine_type = 'restaurants'
    yelp_result_list = []
    yelp_search_params = {'term': cuisine_type, 'location': ''}
    for d in location_dict_list:
        yelp_search_params['location'] = d['location']
        yelp_request = requests.get(yelp_search_url, params=yelp_search_params, headers=yelp_headers)
        yelp_search_result = json.loads(yelp_request.text)
        #print(yelp_search_result)
        for b in yelp_search_result['businesses']:
            b['site_id'] = d['site_id']
        yelp_result_list.append(yelp_search_result)
    return yelp_result_list

if ('yelp_result_list' in CACHE_DICT.keys()):
    print("Using cache")
    yelp_result_result = CACHE_DICT['yelp_result_list']
else:
    print("Fetching")
    yelp_result_list = search_on_yelp()
    CACHE_DICT['yelp_result_list'] = yelp_result_list
    save_cache(CACHE_DICT)
#print(yelp_result_list) #COMMENT OUT

#IMPORTANT DATA LOADING: LOADING SITES AND YELP DATA
def load_sites():
    insert_site_sql = '''
        INSERT INTO Sites
        VALUES (NULL, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for a in sites_list:
        if a != {}:
            cur.execute(insert_site_sql, 
                [
                    a['site_name'],
                    a['street'],
                    a['city'],
                    a['region_zip']
                ]
            )
    conn.commit()
    conn.close()


def load_yelp():
    insert_yelp_sql = '''
        INSERT INTO Restaurants
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for y in yelp_result_list:
        business_list = y['businesses']
        for b in business_list:
            category_list = b['categories']
            titles = []
            for c in category_list:
                category_title = c['title']
                titles.append(category_title)
            category_joined = (', ').join(titles)
            if 'price' in b.keys():
                price = b['price']
            else:
                price = 'No price info'
            cur.execute(insert_yelp_sql,
                [
                    b['name'],
                    b['is_closed'],
                    b['review_count'],
                    category_joined,
                    b['rating'],
                    price,
                    b['location']['address1'],
                    b['location']['address2'],
                    b['location']['address3'],
                    b['location']['city'],
                    b['location']['zip_code'],
                    b['location']['state'],
                    b['phone'],
                    b['site_id']
                ]
            )
    conn.commit()
    conn.close()

#IMPORTANT IMPLEMENTATION: CALLING DATA LOADING FUNCTIONS, COMMENT OUT LATER
#load_sites()
#load_yelp()

def process_command(command, site_name):
    '''TODO
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    data_type_list = ['byreviewcount', 'bycategory', 'byrating', 'byprice', 'byaddress']
    command = str(command).lower()
    
    input_valid = True
    if command in data_type_list:
        input_valid = True
    else:
        input_valid = False
        return None

    if input_valid == True:
        # if command == 'everything':
        #     statement = "SELECT * "
        if command == 'byreviewcount':
            statement = "SELECT r.RestaurantName, r.ReviewCount "
        elif command == 'bycategory':
            statement = "SELECT r.RestaurantName, r.Category "
        elif command == 'byrating':
            statement = "SELECT r.RestaurantName, r.Rating "
        elif command == 'byprice':
            statement = "SELECT r.RestaurantName, r.Price "
        elif command == 'byaddress':
            statement = "SELECT r.RestaurantName, r.Address1, r.Address2, r.Address3, r.City, r.ZipCode, r.State "
        else:
            return None
        statement += "FROM Restaurants r JOIN Sites s ON r.SiteId = s.SiteId WHERE s.SiteName=?"

    site_name = [str(site_name)]
    table_return_list = cur.execute(statement, site_name)
    conn.commit()
    for row in table_return_list:
        print(row)
    conn.close()
    return table_return_list
    

if __name__ == "__main__":
    get_state = input("Please select a state from the four most popular tourism states\n(california, florida, nevada, texas)\nor \"exit\"\n: ")
    get_state = str(get_state).lower()
    while get_state != 'exit':
        if get_state not in states:
            print('[Error] Please choose a state from the four most popular tourism states')
            get_state = input("Please select a state from the four most popular tourism states\n(california, florida, nevada, texas, new york)\nor \"exit\"\n: ")
        else:
            print('-------------------------------------------')
            print(f'List of Top Attractions in {get_state}')
            print('-------------------------------------------')
            start_num = 1
            for site in state_sites_dict[get_state]:
                print(f"[{start_num}] {site['site_name']}, {site['region_zip']}")
                start_num += 1

            #for users to look deep into specific attraction site and search for restaurants nearby
            get_num = input('Choose a number to search for nearby restaurants or \"exit\" or \"back\"\n: ')
            get_num = get_num.lower()
            while get_num != 'exit':
                try:
                    get_num = int(get_num)
                    if (get_num not in range(len(state_sites_dict[get_state])+1)):
                        print('[Error] Invalid Input')
                        print('-------------------------------------------')
                        get_num = input('Choose a number to search for nearby restaurants or \"exit\" or \"back\"\n: ')
                except:
                    print('[Error] Invalid Input')
                    print('-------------------------------------------')
                    get_num = input('Choose a number to search for nearby restaurants or \"exit\" or \"back\"\n: ')
                if (get_num in range(len(state_sites_dict[get_state])+1)):
                    get_indice = int(get_num) - 1
                    get_site_name = state_sites_dict[get_state][get_indice]['site_name']

                    print(f"Great! You have chosen \"{get_site_name}\" as your destination.")
                    print("Now please choose how the data would be presented.")
                    print("Choose from (byReviewCount, byCategory, byRating, byPrice, byAddress)")
                    get_command = input("Type in your request (example: byReviewCount) or \"exit\" or \"back\"\n: ")
                    get_command = str(get_command).lower()
                    while get_command != 'exit':
                        if get_command != 'back':
                            command_result = process_command(get_command, get_site_name)
                            if command_result == None:
                                print("Sorry, no data found for your search.")
                                get_command = input("Type in your request (example: byReviewCount) or \"exit\" or \"back\"\n: ")
                            else:
                                process_command(get_command, get_site_name)
                                get_command = input("Type in your request (example: byReviewCount) or \"exit\" or \"back\"\n: ")
                        else:
                            get_num = input('Choose a number to search for nearby restaurants or \"exit\" or \"back\"\n: ')
                            break
                    else:
                        exit()

                if get_num == 'back':
                    get_state = input("Please select a state from the four most popular tourism states\n(california, florida, nevada, texas)\nor \"exit\"\n: ")
                    break
            else:
                exit()
    else:
        exit()               


                    



