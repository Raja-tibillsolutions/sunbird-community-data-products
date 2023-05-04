import requests
import datetime

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
        totalCount
        nodes {
          createdAt
          author{
            login
          }
          comments(first:100){
            nodes{
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
headers = {"Authorization": "bearer " + token_details}

# Get start and end dates from the user
start_date = input("Enter start date (YYYY-MM-DD): ")
end_date = input("Enter end date (YYYY-MM-DD): ")

# Convert start and end dates to datetime objects
start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()

# Set initial cursor to null
cursor = None

# Initialize discussion and user counts to 0
discussion_count = 0
new_user_count = 0
seen_users = set()
# seen_users = set(seen_users1)
user_counts_by_date = {}

while True or False:
    # Set variables for GraphQL query
    variables = {"cursor": cursor}

    # Send request to GitHub API
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})

    # Check if request was successful
    if response.status_code != 200:
        print(f"Error fetching discussion threads. Status code: {response.status_code}")
        break

    # Parse response data
    data = response.json()
    # print(data)

    # Count the number of discussions created within the specified date range
    for discussion in data['data']['repository']['discussions']['nodes']:
        created_at = datetime.datetime.strptime(discussion['createdAt'], '%Y-%m-%dT%H:%M:%SZ').date()
        if start_date <= created_at <= end_date:
            discussion_count += 1
            print(f"Discussion created on {created_at}")

            # Add the author of the discussion to the seen users set
            author = discussion['author']['login']
            seen_users.add(author)

            # Increment the count for the current date in the user_counts_by_date dictionary

            if created_at in user_counts_by_date:
                user_counts_by_date[created_at] += 1
            else:
                user_counts_by_date[created_at] = 1
            new_user_count += 1

    # Check if there are more pages of data to fetch
    if data['data']['repository']['discussions']['pageInfo']['hasNextPage']:
        cursor = data['data']['repository']['discussions']['pageInfo']['endCursor']
    else:
        break

# Get the total count of users
total_user_count = len(seen_users)


print(seen_users)
print(f"Number of discussions created between {start_date} and {end_date}: {discussion_count}")
print(f"Number of discussions created between {start_date} and {end_date}: {user_counts_by_date}")
print(f"Number of users created between {start_date} and {end_date}: {new_user_count}")

