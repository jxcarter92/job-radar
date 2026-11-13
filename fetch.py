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

    pay = job_details["PositionRemuneration"]# declare the list with pay variable

    if pay:#dont need len(pay) since if pay is same as len() > 0
        pay_min = int(float(pay[0]["MinimumRange"]))#one brance below
        pay_max = int(float(pay[0]["MaximumRange"]))
        pay_interval = pay[0]["RateIntervalCode"]
    else: 
        pay_min = None
        pay_max = None
        pay_interval = None

    record = {#variables to return. 
        "job_id": job_details["PositionID"],
        "title": job_details["PositionTitle"],
        "org": job_details["OrganizationName"],
        "location": job_details["PositionLocationDisplay"],
        "pay_min": pay_min,
        "pay_max": pay_max,
        "pay_interval": pay_interval,
        "link": job_details["ApplyURI"][0], 
        "closing_date": job_details["PositionEndDate"]
    }

    return record

def score_pay(record):#score system for max pay -> record is the parameter. Same naming convention used in to_record
    pay_max = record["pay_max"]#varaible for max pay
    pay_interval = record["pay_interval"]#variable for hourly pay

    if pay_max is None:#is there any pay associated with job
        return 5
    if pay_interval == "PH":
        pay_max = pay_max * 2080
    if pay_max >= 120000:
        return 10
    if pay_max >= 100000:
        return 6
    else:
        return 0

job_list = fetch_jobs()#branches were variables live

for job in job_list:#conveyor belt moving one job at a time. ADD FUNCTIONS TO THIS PART!!!!
    record = to_record(job)# 1. to_record builds a record and returns it
    score = score_pay(record)#2. score_pay builds a rankning system to be returned

    print(record["title"], "->", score)# 3. the loop passes that record to score_pay. Prints title and score for pay
    print(json.dumps(record, indent=4))#prints all records varaibles in API format

