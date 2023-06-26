import json
import pprint
from api.model.db import connect_to_db


# Connect to database
client = connect_to_db()

database = client.locale

# Open JSON file
try:
    with open('nigeria-data.json', 'r') as json_file:
        data = json.load(json_file)
        collection = database.data
        collection.insert_many(data)
except Exception as e:
    print(e)

# Create a new collection for geopolitical zones
geopolitical_zones = database.regions

local_governments = database.local_governments


# Get distinct geopolitical zones with their corresponding states
try:
    geopolitical_zones_states = collection.aggregate([
        {
            "$group": {"_id": "$geo_politcal_zone",
                       "states": {"$addToSet": "$state"}}
        }
    ])


# Insert geopolitical zones and their corresponding states into the new collection
    for geopolitical_zone in geopolitical_zones_states:
        region = {
            "geo_political_zone": geopolitical_zone["_id"],
            "states": geopolitical_zone["states"]
        }
        geopolitical_zones.insert_one(region)

except Exception as e:
    print(e)


try:
    for lgas in data:
        state = collection.find_one({"state": lgas["state"]})

        if state:
            local_government_area = {
                "lga": lgas["lgas"],
                "state_id": state["_id"],
                "state": state["state"]
            }
            local_governments.insert_one(local_government_area)
        else:
            print("State not found")
except Exception as e:
    print(e)


# client.close()
