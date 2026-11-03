import os
import requests

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

for job in data["SearchResult"]["SearchResultItems"]:#7. Print resutl of positionTitle
    print(job["MatchedObjectDescriptor"]["PositionTitle"])
