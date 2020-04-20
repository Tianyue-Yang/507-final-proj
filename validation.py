import secrets
import requests
import sqlite3
import json
from bs4 import BeautifulSoup

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


#res_category_list = ['newamerican', 'tradamerican', 'breakfast_brunch', 'buffets', 'burgers', 'cafes', 'cafeteria', 'chinese', 'hotdogs', 'food_court', 'japanese', 'mexican', 'pizza', 'vegan']
cuisine_type = 'restaurants'
#search_location = 'MI 48103'

#yelp_search_params = {'term': cuisine_type, 'location': search_location}
# yelp_search_request = requests.get(yelp_search_url, params=yelp_search_params, headers=yelp_headers)
# yelp_search_result = json.loads(yelp_search_request.text)
#print(yelp_search_result)

CACHE_DICT = load_cache()
state_for_attraction = 'michigan'
attraction_base_url = 'https://www.attractionsofamerica.com/attractions/'
attraction_url = attraction_base_url + state_for_attraction + '.php'
#attraction_response = requests.get(attraction_url).text
attraction_response = make_url_request_using_cache(attraction_url, CACHE_DICT)
soup = BeautifulSoup(attraction_response, 'html.parser')
#print(soup)

attrac_location_containers = soup.find_all('div', class_='box_style_1')
#print(attrac_location_containers)
attrac_list = []
attrac_location_list = []
for container in attrac_location_containers:
    attrac_dict = {}
    attrac_parent = container.find('div', class_='pl10 pr10 pb10')
    if attrac_parent != None:
        attrac = attrac_parent.find('h2').text.split(': ')[1]
        attrac_dict['site_name'] = attrac
    location_source = container.find('p', class_='pl10 pr10 inner-titles-post')
    if location_source != None:
        got_location = location_source.text.split(' ')[1:]
        attrac_location = ' '.join(got_location)
        attrac_location_list.append(attrac_location)
        attrac_dict['region_zip'] = attrac_location.split(', ')[-1]
        attrac_dict['city'] = attrac_location.split(', ')[-2]
        if len(attrac_location.split(', ')) >= 3:
            attrac_dict['street'] = attrac_location.split(', ')[-3]
        else:
            attrac_dict['street'] = 'No street data'

    attrac_list.append(attrac_dict)

#print(attrac_location_list)
#print(attrac_list)
#print(attrac_location_list)
location_dict_list = []
for location in attrac_location_list:
    attrac_location_dict = {}
    attrac_location_dict['location'] = location
    attrac_location_dict['site_id'] = attrac_location_list.index(location)+1
    location_dict_list.append(attrac_location_dict)

#print(f'LOCATION DICT LIST: {location_dict_list}')

#SEARCHING ON YELP FUSION 
yelp_result_list = []
yelp_search_params = {'term': cuisine_type, 'location': ''}
for d in location_dict_list:
    yelp_search_params['location'] = d['location']
    yelp_search_request = requests.get(yelp_search_url, params=yelp_search_params, headers=yelp_headers)
    yelp_search_result = json.loads(yelp_search_request.text)
    for b in yelp_search_result['businesses']:
        b['site_id'] = d['site_id']
    yelp_result_list.append(yelp_search_result)

#print(yelp_result_list)

#CREATING DB TABLES
DB_NAME = 'site_restaurant.sqlite'
# def create_db():
#     conn = sqlite3.connect(DB_NAME)
#     cur = conn.cursor()

#     drop_sites_sql = 'DROP TABLE IF EXISTS "Sites"'
#     drop_restaurants_sql = 'DROP TABLE IF EXISTS "Restaurants"'

#     create_sites_sql = 

#LOAD SITE DATA INTO TABLES
def load_sites():
    insert_site_sql = '''
        INSERT INTO Sites
        VALUES (NULL, ?, ?, ?, ?)
    '''

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for a in attrac_list:
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
# load_sites() #IMPORTANT IMPLEMENTATION

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

load_yelp() #IMPORTANT IMPLEMENTATION



