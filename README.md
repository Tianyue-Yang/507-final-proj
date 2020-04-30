# **This is Tianyue's 507 final project.**
This is a travel advisor program made with ❤️ by Tianyue Yang. She's an UX designer who knows some coding.
This program is for you to choose one from the four most popular **tourism states**, to choose an **attraction site** within that state to travel to, and look at the results of nearby **restaurants** sorted by the sorted method you selected.

## Special Requirements
You would need an API key from Yelp Fusion. Visit [https://www.yelp.com/developers/v3/manage_app](https://www.yelp.com/developers/v3/manage_app) to get an API key, and store that API key in a file named "secrets.py".

If you've done the above steps correctly, your secrets.py file should have content similar to this:
api_key = '********************'
## Required packages
import secrets
import requests
import sqlite3
import json
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
## Walkthrough
1. Once you land the homepage, You will see a list of options for you to choose from the four most popular tourism states:
California, Florida, Nevada, Texas
**Please go ahead choose one of those.**

2. After choosing a state, you will see a list of top attraction sites for that state. Please refer to the index number of the attraction site you want to travel to, and go ahead type in **just the index number**  of the attraction site you chose.

***Important Note: Please make sure you enter an index number came from the index number list.**

If you see the error page below after entering an index number, It's because you didn't enter a correct index number came from the index number list shown on you screen. Please go back to the attraction sites list page and re-enter a correct number.

(Error page image)
[https://www.flickr.com/photos/188216931@N04/49835735816/in/dateposted-public/](https://www.flickr.com/photos/188216931@N04/49835735816/in/dateposted-public/)

3. After correctly entered an index number, you will see a series of sort options. Please apply the options as you want and click the "Get Restaurants" button to see restaurant results.
4. Now you are getting the restaurant results! Enjoy.
