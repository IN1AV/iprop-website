import urllib.request
import json
import codecs
import time

# Read entire Steam catalogue in python dict
# With the downloaded file, data["applist"]["apps"] is of length 111460
# File downloaded from http://api.steampowered.com/ISteamApps/GetAppList/v0002/?key=STEAMKEY&format=json
game_list_file = codecs.open("./steam_applist.json", encoding="utf-8")
dict_of_games = json.load(game_list_file)
game_list_file.close()

BASE_URL = "https://store.steampowered.com/api/appdetails?appids="
FILENAME = "./filtered_gamelist.json"

# Variables to control that script is running smoothly
counter = 0
success_counter = 0
reached_last_id = False

# Get appid from the last line of the file
# This assumes the last line is a correctly formatted output from
# a previous run of this script
read_file = codecs.open(FILENAME, "r", encoding="utf-8")
last_line = read_file.read().splitlines()[-1]
read_file.close()
split_last_line = last_line.split(",")
split_id = split_last_line[0].split(":")
last_id = split_id[1]

# Suggest to manually surround the output file with { "games": [ ..... ] }
game_category_file = codecs.open(FILENAME, "a+", encoding="utf-8")

# Main program loop
while True:
    try:
        print(f"Starting requests with last_id: {last_id}")
        for game in dict_of_games["applist"]["apps"]:
            # Get the appid as a str. 
            appid = str(game["appid"])

            # Loop through the list of apps until we find the appid of the latest game we added
            if (not reached_last_id):
                if (appid == last_id):
                    reached_last_id = True
                continue
            
            # Open the url and save the contents as a dict
            response = urllib.request.urlopen(BASE_URL + appid)
            game_data = json.load(response)
            
            # Update last_id so we don't restart at last entry in case of 429 error
            last_id = appid
            counter += 1

            # If the "success" key has value False, there is no "data" dict inside game_data object
            if(game_data[appid]["success"] == False):
                continue
            
            current_game_data = game_data[appid]["data"]

            # Possible types: "game", "dlc", "music", "demo" (and more?)
            game_type = current_game_data["type"]
            if( not (game_type == "game" or game_type == "dlc")):
                # print(appid + ": " + current_game_data["type"])
                continue
            
            # Change double quotes to single quotes to avoid JSON errors
            name = game["name"].replace('"', "'")

            # Get list of developers
            developers = current_game_data.get("developers")
            if (developers == None):
                continue
            developers = repr(developers).replace("'", '"')

            # Get list of publishers
            publishers = current_game_data.get("publishers")
            if (publishers == None):
                continue
            publishers = repr(publishers).replace("'", '"')

            # Some (actually most) games don't have a metacritic score.
            # As this is a requirement for the database, ignore all unscored games
            metacritic = current_game_data.get("metacritic")
            if (metacritic == None):
                continue
            score = metacritic["score"]

            # Some games don't have a genres key. Use .get() to avoid KeyErrors
            genres = current_game_data.get("genres")
            if (genres == None):
                continue
            # Convert genres to string to replace all single quotes with double quotes
            genres = repr(genres).replace("'", '"')

            release_date = current_game_data["release_date"]
            release_date = repr(release_date).replace("'", '"').replace("True", "true").replace("False", "false")

            formatted_str = f'"appid":{appid}, "type":"{game_type}", "name":"{name}", "developers":{developers}, "publishers":{publishers}, "score":{score}, "genres":{genres}, "release_date":{release_date}'

            # Write desired contents to file
            game_category_file.write("{" + formatted_str + "},\n")
            
            # Control to see if script is still running
            success_counter += 1
            time.sleep(0.4)
    
    except urllib.error.HTTPError as e:
        print(f"Received error \"{e}\" at {time.asctime(time.localtime(time.time()))}")
        print(f"Pulled {counter} requests in current program runtime, of which {success_counter} were successfully added to the file")
        # Close file to properly commit all changes
        game_category_file.close()
        # If the reason for failing is not 'Too many requests', exit to avoid messing up the file
        if (e.code != 429):
            exit()
        
        reached_last_id = False
        print(f"last_id is: {last_id}")
        # In current setup with sleep(0.4) after each url-grab, waiting ~200 seconds
        # after 429 error seems to be the sweet spot. 180 or lower immediately
        # runs into 429 again, causing it to wait twice
        time.sleep(200)
        # Re-open file to restart appending game data
        game_category_file = codecs.open(FILENAME, "a+", encoding="utf-8")

