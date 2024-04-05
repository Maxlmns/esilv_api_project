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


@app.route('/links') # Route to show all the links found about AI
def links():
    try: # If the file is not found we will return an empty list
        with open(FILENAME, "r") as f:
            links = json.load(f)
    except FileNotFoundError:
        links = []
    return render_template('links.html', links=links)

@app.route('/chat', methods=['GET', 'POST']) # Route to chat with an AI, see utils.py for the chat_bot function, Careful it takes some time to get the response
def chat():
    response = ""
    if request.method == 'POST':
        query = request.form.get('query') # Get the query from the form
        response = chat_bot(query)  
    return render_template('chat.html', response=response)  

@app.route('/summarize', methods=['GET', 'POST']) # Route to summarize an article
def summarize():
    response = ""
    if request.method == 'POST':
        query = request.form.get('query') # User will input the link of the article
        response = find_content(query) # We will get the content of the article
        if query != "No article found": 
            response = chat_bot("summarize: "+ response, 5)  # We will summarize the article using the chatbot function
    return render_template('summarize.html', response=response)

@app.route('/links/favourite')
def favourites():
    with open(FILENAME, "r") as f:
        links = json.load(f)
    return render_template('favourite.html', link=links[0]) # The first link in the list is the main article on the google news page, we will show it as the favourite

# This route will show the content of the main article, Careful, if the article is not free, no content will be shown
@app.route('/links/favourite/text')
def text():
    with open(FILENAME, "r") as f:
        links = json.load(f)
    text_content = find_content(links[0])  # We will get the content of the main article
    return render_template('text.html', text_content=text_content) # We will show the content of the main article

if __name__ == '__main__':
    app.run(debug=True)
