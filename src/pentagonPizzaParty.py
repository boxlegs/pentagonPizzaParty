import requests
import os
from dotenv import load_dotenv
import populartimes
from datetime import datetime
import pytz
import sys

load_dotenv() 

GCP_API_KEY = os.getenv('GCP_API_KEY')
NTFY_URL = os.getenv('NTFY_URL') # Endpoint e.g. https://ntfy.sh/pentagon
ANOMALY_THRESHOLD = float(os.getenv('THRESHOLD', 1.5)) # Default threshold is 1.5x
PLACE_ID =  "ChIJI6ACK7q2t4kRFcPtFhUuYhU" # Domino's Pizza, 2602 Columbia Pike, Arlington, VA


def get_dominos_data():
    
    # Get current time for comparison
    data = populartimes.get_id(GCP_API_KEY, PLACE_ID)
    if "current_popularity" not in data.keys():
        print("ERROR: Current popularity data is unavailable - Domino's is closed!")
        exit(2)
    
    return data

    
    
    
def publish_notification(content, title, priority, tags):
    
    req = requests.post(NTFY_URL,
    data=content,
    headers={
        "Title": title,
        "Priority": priority,
        "Tags": tags,
        "Markdown": "yes" # Not yet implemented in ntfy
    })
    if req.status_code != 200:
        print(f"Failed to send notification: {req.status_code} - {req.text}")
    

def main():
    
    if len(sys.argv) > 1:
        print("Usage: python3 pentagonPizzaParty.py")
        exit(1)
        
    if not GCP_API_KEY:
        print("GCP_API_KEY is not set - add it to your .env file or .[ba|z|k]shrc config")
        exit(1)
    if not NTFY_URL:
        print("NTFY_URL is not set - add it to your .env file or .[ba|z|k]shrc config.")
        exit(1)
        
    # Get time in Virginia
    current_time = datetime.now(pytz.timezone('America/New_York')) # Use America/New_York for VA
    weekday = current_time.weekday()
    current_day_str = current_time.strftime('%A')  
    current_hour = current_time.hour
    print(f"Current time at the Pentagon: {current_hour % 12}{'PM' if current_hour >= 12 else 'AM'} on {current_day_str}")
    
    data = get_dominos_data()
        
    current_popularity = data["current_popularity"]
    regular_popularity = data["populartimes"][weekday]["data"][current_hour]
    print(f"Current popularity: {current_popularity}, Regular popularity: {regular_popularity}")
    
    if current_popularity/regular_popularity > ANOMALY_THRESHOLD:
        print("High activity detected, sending notification...")
        content = f"Massive spike in Domino's activity at " + \
        f"{current_hour % 12}{'PM' if current_hour >= 12 else 'AM'} by a factor of {current_popularity/regular_popularity:.1f}.\n" + \
        f"Current business is reading {current_popularity}, compared to average activity of {regular_popularity}.\n\n{'Shit is about to get variably real.' if current_popularity/regular_popularity > 2 else ''}"
        
        publish_notification(content=content, # Feel free to edit yourself
            title="MASSIVE ACTIVITY DETECTED at the Pentagon Domino's", 
            priority="urgent", 
            tags="biohazard,pizza")

    return
    
if __name__ == "__main__":
   main()