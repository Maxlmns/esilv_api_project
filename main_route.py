# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 11:41:52 2024

@author: nthom
"""

import requests
from bs4 import BeautifulSoup
import json
import difflib
from flask import Flask, request,render_template
from utils import chat_bot, get_number_articles, find_content

google = "https://news.google.com/search?q=artificial%20intelligence&hl=en-US&gl=US&ceid=US%3Aen" # Get all the articles links from google news about AI
google_article = "https://news.google.com" # The links we got before are relative, we need to add the domain to get the full link
response = requests.get(google) # Get the response from the google news page
FILENAME = r"links.json" # The file where we will store the links
soup = BeautifulSoup(response.text, 'html.parser') # Parse the response
links = soup.find_all("a") # Get all the links from the page

# This part is to save the links in a json file

json_file = [] 
for link in links:
    href = link.get("href")
    if href and href.startswith("./articles"):  
        json_file.append(google_article + href)

with open(FILENAME, "w") as f: # To avoid saving all the old links we will overwrite the file each time we run the app
    json.dump(json_file, f)

routes_links = ["links","chat","summarize","links/favourite","links/favourite/text"] # Define the routes we will use in the app 

app = Flask(__name__, static_url_path='/static') # Create the app

@app.route('/', methods=['GET', 'POST']) # main route
def search_form():
    link = ""
    closest_match = ""
    if request.method == 'POST':
        query = request.form.get('query')
        closest_match = difflib.get_close_matches(query, routes_links, n=1, cutoff=0.01) # We made a search bar to find the routes, we will use difflib to get the closest match. Hence even with a typo the user will get the right route
        if closest_match:
            closest_match = closest_match[0] # Closest match found in the route list
    return render_template('search_form.html', link=closest_match, closest_match=closest_match, routes_links=routes_links, length=get_number_articles()) # Render the template with HTML