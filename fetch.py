import os
import requests
import json

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

# 4. Make the request
response = requests.get("https://data.usajobs.gov/api/search", headers=headers, params=params)

# 5. Turn the reply into a Python dict
data = response.json()

# 6. Print how many jobs came back
print("total jobs listed: " , data["SearchResult"]["SearchResultCount"])

first_job = data["SearchResult"]["SearchResultItems"][0]["MatchedObjectDescriptor"]# print first job in json file.
#print(json.dumps(first_job, indent=4))#displays it in correct shape

for item in data["SearchResult"]["SearchResultItems"]:
    job_details = item["MatchedObjectDescriptor"]

    record = {
        "job_id": job_details["PositionID"],
        "title": job_details["PositionTitle"],
        "org": job_details["OrganizationName"],
        "location": job_details["PositionLocationDisplay"],
        "pay_min": int(job_details["PositionRemuneration"][0]["MinimumRange"]),
        "pay_max": int(job_details["PositionRemuneration"][0]["MaximumRange"]),
        "link": job_details["ApplyURI"][0], 
        "closing_date": job_details["PositionEndDate"]
    }

    print(json.dumps(record, indent=4))

    

