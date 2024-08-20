import pandas as pd
import datetime
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

# Get the current date and time for the log file name
now = datetime.datetime.now()
log_file_name = f"WhatsAppScheduler_{now.strftime('%Y-%m-%d_%H-%M-%S')}.txt"

# Set up logging
logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(message)s')

# Load contacts and greeting messages
contacts_df = pd.read_csv("contacts.csv")

def load_greetings(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]

birthday_wishes = load_greetings("BirthdayWishes.txt")
anniversary_wishes = load_greetings("AnniversaryWishes.txt")

# Configure the Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("user-data-dir=C:/Users/HP/AppData/Local/Google/Chrome/User Data")
chrome_options.add_argument("--profile-directory=Profile 4")
#My user is in profile 4 directory you can find yours by going to Chrome://version
service = Service(executable_path="C:/Users/HP/.cache/selenium/chromedriver/win64/127.0.6533.119/chromedriver.exe")

driver = webdriver.Chrome(service=service, options=chrome_options)

# Open WhatsApp Web
driver.get("http://web.whatsapp.com")
wait = WebDriverWait(driver, 100)
search_box_xpath = '//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div'
#This xpath will help the program to reiterate the for each recipient.
message_box_xpath = '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]'
#This is to send the message. 

def send_message(phone_num, message_text, name):
    try:
        search_box = driver.find_element(By.XPATH, search_box_xpath)
        search_box.clear()
        search_box.send_keys(phone_num)
        search_box.send_keys(Keys.RETURN)

        message_box = wait.until(EC.presence_of_element_located((By.XPATH, message_box_xpath)))
        message_box.send_keys(message_text)
        message_box.send_keys(Keys.ENTER)
        time.sleep(1)  # Small delay to ensure the message is sent before moving on

        # Log the message sent
        logging.info(f"Sent message to {name} {phone_num}: {message_text}")
    except Exception as e:
        logging.error(f"Failed to send message to {name} {phone_num}: {e}")

# Get today's date
today = datetime.datetime.today().strftime("%d-%b")

# Process each contact
for _, contact in contacts_df.iterrows():
    name = contact["Name"]
    phone_num = f"{contact['Code']}{contact['PhoneNumber']}"
    nickname = contact["NickName"]
    group = contact["Group"]
    birthday = contact["Birthday"]
    anniversary = contact["Anniversary"]

    # Determine the name to use
    name_to_use = nickname if nickname != "NA" and group not in ["Colleagues", "Neighbors", "ServiceVendors"] else name

    message_text = None
    # Check if today is the person's birthday
    if birthday == today:
        message_text = random.choice(birthday_wishes).replace("[Name]", name_to_use)

    # Check if today is the person's anniversary
    elif anniversary == today:
        # Send an anniversary reminder to yourself
        message_text = f"Send Message to {name_to_use} \n {random.choice(anniversary_wishes).replace('[Couple’s Name]', name_to_use)}"
        phone_num = "{MyPersonalNumber}"

    # Check for New Year's or a specific festival
    #Below section we can tweak to send bulk messages to everyone. 
    elif today == "01-Jan":
        festival_message = "Happy New Year [Name]! 🎉 Wishing you a year full of joy, success, and good health!"
        message_text = festival_message.replace("[Name]", name_to_use)

    if message_text:
        send_message(phone_num, message_text, name_to_use)

# Close the browser
logging.error(f"All messages are sent successfully")
driver.quit() 
