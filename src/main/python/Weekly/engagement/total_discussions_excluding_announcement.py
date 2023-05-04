import json
import requests
from datetime import datetime

import configparser

config = configparser.ConfigParser(interpolation=None)
config.read("config.ini")

name_of_community = config.get("community_name", "name")

# Get user input for start and end date
start_date_str = input("Enter start date (YYYY-MM-DD): ")
end_date_str = input("Enter end date (YYYY-MM-DD): ")

# Convert user input to datetime objects
start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

# Calculate the end of the end date (since the query uses an inclusive range)
end_date_end = end_date.replace(hour=23, minute=59, second=59)

# Format dates as ISO 8601 strings for use in the query
start_date_iso = start_date.isoformat() + "Z"
end_date_iso = end_date_end.isoformat() + "Z"

# Construct the query string
query = """
query($cursor: String) {
  repository(owner: "%s", name: "community") {
    discussions(first: 100, after: $cursor) {
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        id
        createdAt
        category {
          slug
        }
      }
    }
  }
}
""" % name_of_community
token_details = config.get("bearer", "token")

url = 'https://api.github.com/graphql'
headers = {"Authorization": "bearer " + token_details}

has_next_page = True
end_cursor = None
category_counts = {}
discussions_seen = set()

while has_next_page:
    variables = {"cursor": end_cursor}
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})

    if response.status_code == 200:
        json_data = json.loads(response.text)
        discussions = json_data["data"]["repository"]["discussions"]
        end_cursor = discussions["pageInfo"]["endCursor"]
        has_next_page = discussions["pageInfo"]["hasNextPage"]
        for discussion in discussions["nodes"]:
            category_slug = discussion["category"]["slug"]
            created_at_str = discussion["createdAt"]
            created_at = datetime.fromisoformat(created_at_str[:-1])  # Remove trailing "Z" and convert to datetime
            if category_slug == "announcements":
                continue  # Skip this discussion if it's in the "announcements" category
            if category_slug not in category_counts:
                category_counts[category_slug] = 0
            if discussion["id"] not in discussions_seen and start_date <= created_at <= end_date_end:
                category_counts[category_slug] += 1
                discussions_seen.add(discussion["id"])
    else:
        print("Request failed with status code:", response.status_code)
        break

total_count = sum(category_counts.values())
print(f"Total discussion count from {start_date_str} to {end_date_str}: {total_count}")

print("Discussion counts by category:")
for category_slug, count in category_counts.items():
    print(f"{category_slug}: {count}")

