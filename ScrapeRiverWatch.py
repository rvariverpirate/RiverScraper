# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 18:23:10 2018

@author: joseph.cannella
Refferences: https://www.dataquest.io/blog/web-scraping-tutorial-python/

"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
import time
import datetime
import lxml


# Function for removing prefix form string
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever

# Loop forever to keep updating the page
while(1):
    try:
        try:
            # Make GET request to the River Watch web page
            riverPage = requests.get("http://jamesriverwatch.org/")
            
            # Initialize Beautiful Soup to get the page content
            riverSoup = BeautifulSoup(riverPage.content, 'html.parser')
            #script = soup.find_all('script', attrs={'type':"text/javascript"})[7]
            
            # Extract only the "ratData" variable
            jsObject = re.search("var ratData = {(.*)}]};", str(riverSoup)).group(0)
            
            # Remove anything outside brackets
            jsonString = remove_prefix(jsObject, "var ratData = ")[:-1].replace("'", '"')
            
            # Convert json strin to json object
            jsonObject = json.loads(jsonString)["flow"]
            
            # Convert the json to Pandas Data Frame
            pandasDF = pd.DataFrame(list(jsonObject))
            
            # Get the location specific data
            riverData = pandasDF[pandasDF["stnm"] == ("James River 42nd Street Access (J22)")]
            
            # Store specific data in variables
            airTemp = riverData["atemp"].values[0]
            waterLevel = riverData["stgval"].values[0]
            waterTemp = riverData["wtempf"].values[0]
            bacteriaLevel = riverData["bact"].values[0]
            swimFlag = riverData["flag"].values[0]
            measurementDate = riverData["sdate"].values[0].split(",")[0]
            print("A")
        except:
            print("James River Watch page failed")
        
        try:
            # Retrieve weather data
            weatherPage = requests.get("https://forecast.weather.gov/MapClick.php?lat=37.5601&lon=-77.4798#.W4b5cOjFiEJ")
            weatherSoup = BeautifulSoup(weatherPage.content, 'html.parser')
            for br in weatherSoup.find_all("br"):
                br.replace_with(" " + br.text)
            
            # Get the current Weather
            currentConditions = weatherSoup.find(id="current_conditions-summary")
            currentWeather = currentConditions.find(class_="myforecast-current").get_text().encode('ascii',errors='ignore')
            currentTemp = currentConditions.find(class_="myforecast-current-lrg").get_text().encode('ascii',errors='ignore')
            
            # Get the Forecast for Today
            seven_day = weatherSoup.find(id="seven-day-forecast")
            forecast_items = seven_day.find_all(class_="tombstone-container")     
            print("B")           
            try:
                # Get Most Recent Forecast Data (Today or Tonight)
                forecast_0 = forecast_items[0]
                period_0 = forecast_0.find(class_="period-name").get_text().encode('ascii',errors='ignore')# Today or Tonight
                short_desc_0 = forecast_0.find(class_="short-desc").get_text().encode('ascii',errors='ignore')
                temp_0 = forecast_0.find(class_="temp").get_text().encode('ascii',errors='ignore')
                img_0 = forecast_0.find("img")
                desc_0 = img_0['title'].encode('ascii',errors='ignore')
                
                # Get Next Most Recent Forecast Data (Tonight or Tommorow)
                forecast_1 = forecast_items[1]
                period_1 = forecast_1.find(class_="period-name").get_text().encode('ascii',errors='ignore')# Tonight or Tommorow
                short_desc_1 = forecast_1.find(class_="short-desc").get_text().encode('ascii',errors='ignore')
                temp_1 = forecast_1.find(class_="temp").get_text().encode('ascii',errors='ignore')
                img_1 = forecast_1.find("img")
                desc_1 = img_1['title'].encode('ascii',errors='ignore')
                print("C")
            
            except:# some kind of advisory is in place, need to skip it to avoid errors
                # Get Most Recent Forecast Data (Today or Tonight)
                print("Advisory in Effect")
                forecast_0 = forecast_items[1]
                period_0 = forecast_0.find(class_="period-name").get_text().encode('ascii',errors='ignore')# Today or Tonight
                short_desc_0 = forecast_0.find(class_="short-desc").get_text().encode('ascii',errors='ignore')
                temp_0 = forecast_0.find(class_="temp").get_text().encode('ascii',errors='ignore')
                img_0 = forecast_0.find("img")
                desc_0 = img_0['title'].encode('ascii',errors='ignore')
                
                # Get Next Most Recent Forecast Data (Tonight or Tommorow)
                forecast_1 = forecast_items[2]
                period_1 = forecast_1.find(class_="period-name").get_text().encode('ascii',errors='ignore')# Tonight or Tommorow
                short_desc_1 = forecast_1.find(class_="short-desc").get_text().encode('ascii',errors='ignore')
                temp_1 = forecast_1.find(class_="temp").get_text().encode('ascii',errors='ignore')
                img_1 = forecast_1.find("img")
                desc_1 = img_1['title'].encode('ascii',errors='ignore')
                
            
            
        except:
            print("Weather page Failed")
        
        try:
            # Get most recent Water Level Data
            waterPage = requests.get("https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=rmdv2&output=xml")         
            waterSoup = BeautifulSoup(waterPage.content, 'lxml')
            
            observed = waterSoup.find_all('observed')[1].find_all("datum")[0]
            waterLevel = observed.find("primary").get_text()
            print("D")
        except:
            print("Hydrology page failed")
        
        
        # Create the full string to store in text doc for ESP8266 to read
        
        htmlHeader = "<!doctype html><html><head></head><p>"
        pCloseTag = "</p>"
        htmlFooter = "</b></html>"
        LCD_width = "                "
        fullMessage = htmlHeader + "Current Weather: " + str(currentWeather) + " " + str(currentTemp) + LCD_width +  "River Data: Water Temp " + str(waterTemp) + " F, "  + \
        "Bacteria Level " + str(bacteriaLevel) + ", Water level " + str(waterLevel) + " ft, Measured " + str(measurementDate) + LCD_width + " Forecast: " + str(period_0) + " " + str(short_desc_0) + " " + str(temp_0) + ", " + \
        str(period_1) + " " + str(short_desc_1) + " " + str(temp_1) + pCloseTag  + "\n <b>" + str(datetime.datetime.now()) + htmlFooter
        fullMessage = fullMessage.replace("b'", "").replace("'", "")
        print(fullMessage)
        
        f = open("../../Website/dist/assets/data/RiverInfo.html", "w")
        print("E")
        f.write(fullMessage)
        f.close()
    
    except:
        print("Error, something failed")
    
    
    #break# only for debug purposes
    # Wait 30 (s) before updating the page
    time.sleep(30)
