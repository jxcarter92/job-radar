import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def fetch_jobs():
    # 1. Read the key and email from environment variables
    api_key = os.environ["USAJOBS_KEY"]
    email = os.environ["USAJOBS_EMAIL"]

    # 2. Headers: the same three you used with curl
    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": email,
        "Authorization-Key": api_key,
    }

    # 3. Search filters: the same as your URL, but as a dict
    params = {
        "JobCategoryCode": 2210,
        "LocationName": "Austin, Texas",
    }

    response = requests.get("https://data.usajobs.gov/api/search", headers=headers, params=params)

    # 5. Turn the reply into a Python dict
    data = response.json()
    job_list = data["SearchResult"]["SearchResultItems"]

    # 6. Print how many jobs came back
    print("total jobs listed: " , data["SearchResult"]["SearchResultCount"])

    return job_list

    
def to_record(job): #create fucntion to return record of jobs

    job_details = job["MatchedObjectDescriptor"]#top branch of api

    record = {#variables to return. 
        "job_id": job_details["PositionID"],
        "title": job_details["PositionTitle"],
        "org": job_details["OrganizationName"],
        "location": job_details["PositionLocationDisplay"],
        "pay_min": int(float(job_details["PositionRemuneration"][0]["MinimumRange"])),
        "pay_max": int(float(job_details["PositionRemuneration"][0]["MaximumRange"])),
        "link": job_details["ApplyURI"][0], 
        "closing_date": job_details["PositionEndDate"]
    }

    return record

job_list = fetch_jobs()#branches were variables live

for job in job_list:
    record = to_record(job)
    print(json.dumps(record, indent=4))
    

    

