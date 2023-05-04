import json
import requests
from datetime import datetime, timedelta

import configparser

config = configparser.ConfigParser(interpolation=None)
config.read("config.ini")

name_of_community = config.get("community_name", "name")

query = """
query ($cursor: String) {
    repository(owner: "%s", name: "community") {
      discussions(first: 100, after: $cursor) {
        pageInfo {
          hasNextPage
          endCursor
        }
    nodes{
          id
          createdAt
          author{
            login
          }
          comments(first:1){
            nodes{
              createdAt
              author{
                login
              }
            }
          }
        }
      }
    }
}
""" % name_of_community
token_details = config.get("bearer", "token")

url = 'https://api.github.com/graphql'
headers = {"Authorization": "bearer " +token_details}

cursor = None
unique_users = set()
start_date_str = input("Enter start date (YYYY-MM-DD): ")
end_date_str = input("Enter end date (YYYY-MM-DD): ")
start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)

while True:
    variables = {'cursor': cursor}
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
    if response.status_code == 200:
        json_data = json.loads(response.text)
        discussions = json_data["data"]["repository"]["discussions"]["nodes"]
        for d in discussions:
            if d["comments"]["nodes"]:
                posted_time = datetime.strptime(d["createdAt"], '%Y-%m-%dT%H:%M:%SZ')
                if start_date <= posted_time <= end_date:
                    unique_users.add(d["author"]["login"])
                    for c in d["comments"]["nodes"]:
                        comment_time = datetime.strptime(c["createdAt"], '%Y-%m-%dT%H:%M:%SZ')
                        if start_date <= comment_time <= end_date:
                            unique_users.add(c["author"]["login"])
        has_next_page = json_data["data"]["repository"]["discussions"]["pageInfo"]["hasNextPage"]
        if has_next_page:
            cursor = json_data["data"]["repository"]["discussions"]["pageInfo"]["endCursor"]
        else:
            break
    else:
        print("Request failed with status code:", response.status_code)
        break

weekly_active_users = len(unique_users)
print(f"Weekly Active Users: {weekly_active_users}")

