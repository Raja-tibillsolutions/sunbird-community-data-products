import requests
import json
from datetime import datetime

import configparser

config = configparser.ConfigParser(interpolation=None)
config.read("Please provide the file location path")

name_of_community = config.get("COMMUNITY_NAME", "name")


# define the GraphQL query
query = """
query ($cursor: String) {
  repository(owner: "%s", name: "community") {
    discussions(first: 100, after: $cursor) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        createdAt
        locked
      }
    }
  }
}
""" % name_of_community
token_details = config.get("BEARER", "token")

# set up HTTP headers
url = "https://api.github.com/graphql"
headers = {"Authorization": "Bearer "+ token_details}

def count_open_discussions(start_date, end_date):
    # set up GraphQL variables
    variables = {"cursor": None}

    # convert input dates to datetime objects
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    # initialize counter
    count = 0

    # loop through paginated GraphQL responses
    while True:
        response = requests.post(url, headers=headers, json={"query": query, "variables": variables})
        json_response = json.loads(response.text)
        discussions = json_response['data']['repository']['discussions']['nodes']
        for discussion in discussions:
            if not discussion['locked']:
                created_at_str = discussion['createdAt']
                created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
                if start_date <= created_at <= end_date:
                    count += 1
        if not json_response['data']['repository']['discussions']['pageInfo']['hasNextPage']:
            break
        variables["cursor"] = json_response['data']['repository']['discussions']['pageInfo']['endCursor']

    return count

# prompt user for number of date ranges to count
num_ranges = int(input("Enter the number of date ranges to count: "))

# loop through each date range and count the discussions
total_count = 0
for i in range(num_ranges):
    start_date_str = input(f"Enter start date {i+1} in YYYY-MM-DD format: ")
    end_date_str = input(f"Enter end date {i+1} in YYYY-MM-DD format: ")
    count = count_open_discussions(start_date_str, end_date_str)
    total_count += count
    print(f"Total number of open discussions between {start_date_str} and {end_date_str}: {count}")

# display total count
print(f"Total number of open discussions: {total_count}")
