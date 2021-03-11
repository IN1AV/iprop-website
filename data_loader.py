import urllib.request
import json
import codecs
import time

# Read entire Steam catalogue in python dict
# With the downloaded file, data["applist"]["apps"] is of length 111460
# File downloaded from http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json
game_list_file = codecs.open("./steam_applist.json", encoding="utf-8")
data = json.load(game_list_file)
game_list_file.close()

BASE_URL = "https://store.steampowered.com/api/appdetails?appids="
FILENAME = "./filtered_gamelist.json"

# Variables to control that script is running smoothly
counter = 0
reached_old_end = False

# Get appid from the last line of the file
# This assumes the last line is a correctly formatted output from
# a previous run of this script
read_file = codecs.open(FILENAME, "r", encoding="utf-8")
last_line = read_file.read().splitlines()[-1]
read_file.close()
split_last_line = last_line.split(",")
split_id = split_last_line[0].split(":")
old_end_id = split_id[1]

# Might want to surround the contents with { "games": [ ..... ] }
game_category_file = codecs.open(FILENAME, "a+", encoding="utf-8")


while True:
    try:
        print(f"Starting requests with old_end_id: {old_end_id}")
        for game in data["applist"]["apps"]:
            # Get the appid as a str and load the JSON data from the url into a dict
            appid = str(game["appid"])

            # Loop through the list of apps until we find the appid of the latest game we added
            if (not reached_old_end):
                if (appid == old_end_id):
                    reached_old_end = True
                continue
            
            # Open the url and save the contents as a dict
            response = urllib.request.urlopen(BASE_URL + appid)
            game_data = json.load(response)
            
            # If the "success" key has value False, there is no "data" dict inside game_data object
            if(game_data[appid]["success"] == False):
                # print(game_data)
                continue
            
            # Possible types: "game", "dlc", "music", "demo" (and more?)
            game_type = game_data[appid]["data"]["type"]
            if( not (game_type == "game" or game_type == "dlc")):
                # print(appid + ": " + game_data[appid]["data"]["type"])
                continue
            
            name = game["name"]
            # Even with success == True, some games don't have a genres key. Use .get() to avoid KeyErrors
            genres = game_data[appid]["data"].get("genres")
            if (genres == None):
                continue
            # Convert genres to string to replace all single quotes with double quotes
            genres = repr(genres).replace("'", '"')

            formatted_str = f'"appid":{appid}, "name":"{name}", "type":"{game_type}", "genres":{genres}'

            # Write desired contents to file
            game_category_file.write("{" + formatted_str + "},\n")
            
            # Control to see if script is still running
            counter += 1
            time.sleep(0.4)
    
    except urllib.error.HTTPError as e:
        print(f"Received error \"{e}\" at {time.asctime(time.localtime(time.time()))}")
        print(f"Pulled {counter} requests in current program runtime")
        # Close file to properly commit all changes
        game_category_file.close()
        # If the reason for failing is not 'Too many requests', exit to avoid messing up the file
        if (e.code != 429):
            exit()
        # Re-open file in read-only mode to get the last line
        read_file = codecs.open(FILENAME, "r", encoding="utf-8")
        last_line = read_file.read().splitlines()[-1]
        # Close the file again
        read_file.close()
        # Get last line appid
        split_last_line = last_line.split(",")
        split_id = split_last_line[0].split(":")
        end_id = split_id[1]
        old_end_id = end_id
        reached_old_end = False
        print(f"end_id is: {end_id}")
        # In current setup with sleep(0.4) after each url-grab, waiting 3 minutes
        # after 429 error seems to be the sweet spot. 150 or lower immediately
        # runs into 429 again, causing it to wait twice
        time.sleep(180)
        # Re-open file to restart appending game data
        game_category_file = codecs.open(FILENAME, "a+", encoding="utf-8")

