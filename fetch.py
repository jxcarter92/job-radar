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

CLEARANCE_POINTS = {#values USA_JOBS lists their clearance level and my personal score for each
    "top secret": 10,
    "q-clearance": 10,
    "secret": 8,
    "sensitive compartmented information": 8,#sci higher on the same ladder. extra access on top of TS
    "confidential": 5,
    "not required": 3,
    "other": 3,
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
    clearance = job_details["UserArea"]["Details"]["SecurityClearance"]#security clearance is tucked a few levels deeper than any other variable so far. 

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
        "clearance": clearance,
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

def score_clearance(record):#same function as other score defs
    clearance_level = record["clearance"].lower()
    best_score = 0
    best_match = None

    for level, points in CLEARANCE_POINTS.items():
        if level in clearance_level and points > best_score:
            best_score = points
            best_match = level

    return best_score, best_match

results = []#empty list for variables I want displayed. 

job_list = fetch_jobs()#

for job in job_list:#
    record = to_record(job)#list of all the jobs and the vairiables I chose from the api
    pay_score = score_pay(record)#score fucntion for jobs pay
    loc_score, loc_match = score_location(record)#location match and score determind from LOCATION_POINTS
    kw_score, kw_match = score_keywords(record)#keywords of the job title and score determind by KEYWORD_POINTS
    cl_score, cl_level = score_clearance(record)#clearance level and score determind by CLEARANVE_POINTS
    total = pay_score + loc_score + kw_score + cl_score#sum of all the scores

    results.append({#variables I want displayed 
        "title": record["title"],
        "total": total,
        "pay": pay_score,
        "location": loc_score,
        "location_match": loc_match,
        "keyword": kw_score,
        "keyword_match": kw_match,
        "link": record["link"],
        "clearance": cl_score,
        "clearance_level": cl_level,
    })

ranked = sorted(results, key=lambda job: job["total"], reverse=True)#lambda one time helper like the key=key=lambda job: job["total"]. Small function instead of writine def get_total(job)
for job in ranked[:5]:#return only 5 of the top jobs
    print("total score for job:",job["total"], " ", job["title"])
    print("    pay:", job["pay"], "| location:", job["location"], "(", job["location_match"], ")", "| keyword:", job["keyword"], "(", job["keyword_match"], ")", "| Clearance:",  job["clearance"], "(", job["clearance_level"], ")")#Clean print want to display PAY_VARiABLES better
    print("   ", job["link"])