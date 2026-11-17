import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

#dicts to loop through in score_location(record) and score_keywords(record):
LOCATION_POINTS = {#locations and their scores
    "austin, texas": 10,
    "remote": 8,
    "new mexico": 5,
    "location negotiable": 3,
}

KEYWORD_POINTS = {#title of jobs and their score 
    "devsecops": 10,#top job search
    "devops": 9,
    "cloud": 8,
    "software": 8,
    "site reliability": 8,
    "cybersecurity": 7,
    "automation": 7,
    "infrastructure": 7,
    "platform": 7,
}

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

    cities = []
    for location in job_details["PositionLocation"]:
        cities.append(location["LocationName"])

    record = {#variables to return. 
        "job_id": job_details["PositionID"],
        "title": job_details["PositionTitle"],
        "org": job_details["OrganizationName"],
        "location": job_details["PositionLocationDisplay"],
        "cities": cities,
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

def score_location(record):
    cities = record["cities"]
    location = record["location"]
    best_score = 0#start at 0 so if nothing matches it returns 0
    best_match = None

    for text in cities + [location]:#loop through both cities and locations in records
        text_lower = text.lower()#convert everything to lowercase
        for place, points in LOCATION_POINTS.items():#loop through each: ("austin, texas", 10), ... Key: Value in LOCATION_POINTS
            if place in text_lower and points > best_score:
                best_score = points
                best_match = text
        
    return best_score, best_match#return best score and city 
    
def score_keywords(record):
    title = record["title"].lower()#convert to lowercase
    best_score = 0
    best_match = None

    for keyword, points in KEYWORD_POINTS.items():#loop throug to find the match in job title and its score form KEYWORD_POINTS
        if keyword in title and points > best_score:#conditions to match title and score
            best_score = points
            best_match = keyword

    return best_score, best_match



job_list = fetch_jobs()#branches were variables live

for job in job_list:#conveyor belt moving one job at a time. ADD FUNCTIONS TO THIS PART!!!!
    record = to_record(job)# 1. to_record builds a record and returns it
    pay_score = score_pay(record)#2. score_pay builds a rankning system to be returned
    points, reason = score_location(record)#returning a tuple and unpacking
    kw_rating, kw_role = score_keywords(record)

    print(record["title"])#title of job
    print("  pay:", pay_score, "| location:", points, "(", reason, ")", "| title:" , kw_rating, "(" , kw_role, ")")#print pay, location score, city, title score, keyword in title
    print(json.dumps(record, indent=4))#prints all records varaibles in API format

