#!/usr/bin/env python
# coding: utf-8

# In[3]:


# Selenium Import's Librarys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# In[4]:


#Time Library For Sleep Mode 
import time
#For Special Signs
import re
#Create DataFrame
import pandas as pd
#Create Table
import csv
#For Requests Google
from pytrends.request import TrendReq

#Starting Using Selenium For Crawling Process
driver = webdriver.Chrome()

#Create The Arrays That the Data Will Be Saved in Them : Lines For The Table And Text For Columns Name
lines = []
text1 = []

# Crawling In The Pages Of The Bitcoin
for i in range(1,2):
    url = "https://nomics.com/assets/btc-bitcoin/history/{}".format(i)
    browser = driver.get(url)
    elements = driver.find_elements(By.TAG_NAME, 'tr')    
    for line in elements:
        if(line.text != 'DATE\nOPEN\nHIGH\nLOW\nCLOSE\nVOLUME'):
            lines.append(line.text)
        else:
            text1.append(line.text)


# In[5]:


#Create The Columns For The Df 
ColumnName = []
Dates1 = []
Open1 = []
High1 = []
Low1 = []
Close1 = []
Volume1 = []

MeanHigh_Low = []
MeanOpen_Close = []
for i in range(0,6):
    # Start Fill The Column Array
    ColumnName.append(text1[0].rsplit('\n')[i])


# In[6]:


#Start Filling Other Arrays 
y = 0
for i in range (0,len(lines)):
    # The Value For Each Array Is Separated And Inset Into The Right Arrays   
    Dates1.append(lines[y].rsplit('\n')[0])
    Open1.append(lines[y].rsplit('\n')[1])
    High1.append(lines[y].rsplit('\n')[2])
    Low1.append(lines[y].rsplit('\n')[3])
    Close1.append(lines[y].rsplit('\n')[4])
    Volume1.append(lines[y].rsplit('\n')[5])
    y = y + 1


# In[7]:


# Delete Special Charcters From the Data
for i in range(0,len(Dates1)):
    Open1[i] = re.sub(r"[$,]","", Open1[i])
    High1[i] = re.sub(r"[$,]","", High1[i])
    Low1[i] = re.sub(r"[$,]","", Low1[i])
    Close1[i] = re.sub(r"[$,]","", Close1[i])
    Volume1[i] = re.sub(r"[$B]","", Volume1[i]) 
    
    #Not Works Yet
    # Convert String To Int 
    int(Open1[i])
    int(High1[i])
    int(Low1[i])
    int(Close1[i])
    float(Volume1[i])


# In[8]:


# Replace Dates Format For Google and Twitter
for i in range(0,len(Dates1)):
    temp = Dates1[i]
    month = temp.rsplit('/')[0]
    if(len(month) == 1):
        month = "0{}".format(month)    
    day = temp.rsplit('/')[1]
    if(len(day) == 1):
        day = "0{}".format(day)
    year = temp.rsplit('/')[2]
    FinelD = "{}-{}-{}".format(year,month,day) 
    Dates1[i] = FinelD


# In[9]:


#Enter New Columns Names Befor Starting
ColumnName.append("MeanHigh_Low")
ColumnName.append("MeanOpen_Close")
ColumnName.append("PyTredsData")
ColumnName.append("UP-DOWN")


# In[10]:


#Fill The Two Mean Array And Save Resukt As Integers
for i in range(0,len(Open1)):
    MeanHigh_Low.append((int(Low1[i]) + int(High1[i]))/2)
    MeanOpen_Close.append((int(Open1[i]) + int(Close1[i]))/2) 


# In[11]:


#Starting Working On Get Data From Google With API
PyTredsData = []
PyTredsDataFull = []

pytrends = TrendReq()
kw_list = ["bitcoin"] 

# build the payload
for i in range(0, len(Dates1)-1):
    timeframe2 ="{} {}".format(Dates1[i+1],Dates1[i])
    pytrends.build_payload(kw_list, timeframe="{} {}".format(Dates1[i+1],Dates1[i]))
    r = pytrends.interest_over_time().mean()
    PyTredsData.append(r)
for i in range(2, len(PyTredsData)):
    PyTredsDataFull.append(PyTredsData[i]["bitcoin"]) #Get Out Only The Bitcoin Data    


# In[12]:


#Add UP or Down Categorial Column 
UpOrDown = []
for i in range(0, len(Open1)):
    if(Open1[i] > Close1[i]):
        UpOrDown.append("DOWN")
    else:
        UpOrDown.append("UP")


# In[13]:


#Add New Column Name For Tweets
ColumnName.append("POS")
ColumnName.append("NEGA")


# In[14]:


# Starting Working On Get Data From Twitter API

#Import Twitter Scraper 
import snscrape.modules.twitter as sntwitter
# Remove Special Charcters From Twitter API Tweet
import re
# Simplified Text Processing TextBlob is a Python library for processing textual data
from textblob import TextBlob

# Tweets For Once 
maxTweets = 50

# count the total 
ListPositive = []
ListNegative =[]

positive = 0
#test
negative = 0
#Loop The Dates Arrays
for x in range(0,len(Dates1)-1):
    # Creating The Lists To Append Tweet Data To
    tweets_list2 = []
    # Using TwitterSearchScraper to scrape data and append tweets to list
    a = Dates1[x]
    b = Dates1[(x+1)]
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper("#bitcoin since:"+ a + "until:"+ b +" -filter:links -filter:replies").get_items()):
        if i > maxTweets:
            break
        else:
            tweets_list2.append(tweet.content)
    
    #Array After Removement 
    Tweets_PerDay_done =[]
    
    #Cleaning The Data
    for i in tweets_list2:
        new_twee = ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", i).split())
        Tweets_PerDay_done.append(new_twee)

    for i in Tweets_PerDay_done:
        #Analze The Data 
        analysis = TextBlob(i)
            # set sentiment
        if analysis.sentiment.polarity > 0:
            positive += 1
        elif analysis.sentiment.polarity < 0:
            negative += 1
        
    ListPositive.append(positive) 
    ListNegative.append(negative)
    #intial one more time
    positive = 0
    #test
    negative = 0                           


# In[15]:


import csv 
rows = zip(Dates1, Open1, High1, Low1, Close1, Volume1, MeanHigh_Low, MeanOpen_Close, PyTredsDataFull, UpOrDown, ListPositive, ListNegative)
with open('BitData_Final.csv', 'w', newline="") as f: 
    write = csv.writer(f) 
    write.writerow(ColumnName)
    for row in rows:
        write.writerow(row)

