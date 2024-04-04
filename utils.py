from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from time import sleep
import requests
from bs4 import BeautifulSoup
import json

FILENAME = r"links.json"

# This chatbot function is a quite simple function but uses a very poweful tool, and works as follows:
# 1. It opens a browser and goes to the perplexity labs website like a human would do
# 2. It sends the input text to the chatbot and waits for 3 seconds
# 3. It gets the response from the chatbot and returns it


def chat_bot(i,t=3): 
    firefox_options = Options()
    firefox_options.add_argument("--headless") # Run the browser in headless mode (without opening the browser window, you can remove this line to see the robot in action)
    driver = webdriver.Firefox(options=firefox_options) # Open the browser
    url = "https://labs.perplexity.ai/" # The chatbot website (free to use, no need to register)
    driver.get(url)
    text_box = "/html/body/div/main/div/div/div[2]/div[2]/div/div/div/div/div/textarea" # this is the xpath of the text box where the user can write the message (you can find it by right clicking on the text box and selecting inspect) 
    send_button = "/html/body/div/main/div/div/div[2]/div[2]/div/div/div/div/div/div[2]/button"
    k = 3
    driver.find_element("xpath", text_box).send_keys(i)
    driver.find_element("xpath", send_button).click() # Send button
    sleep(t)
    response = f"/html/body/div/main/div/div/div[1]/div/div[2]/div/div/div/div[{k}]/div/div/div[1]/div[2]/div/span"
    response = driver.find_element("xpath", response).text
    driver.quit()
    return response

def get_number_articles(): # Get the number of articles in the json file
    with open(FILENAME, "r") as f:
        links = json.load(f)
    return len(links) 


def find_content(url): #Careful, if the article is not free, no content will be shown
    try:
        response = requests.get(url, allow_redirects=True) # Google news uses redirects 
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.find('article') # Get the article
        if article:
            text = article.get_text()
            return text.strip()  # Remove the extra spaces
        else:
            return "No article found"
    except requests.RequestException as e:
        return f"Error: {e}"
