import requests
import datetime
import configparser

config = configparser.ConfigParser(interpolation=None)
config.read("Please provide the location file path")

name_of_community = config.get("COMMUNITY_NAME", "name")

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
          locked
          category{
              name
            }
          }
        }
      }
    }

""" % name_of_community

token_details = config.get("BEARER", "token")

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

# Initialize discussion count to 0
discussion_count = 0

# Initialize locked discussion count to 0
locked_discussion_count = 0

while True:
    # Set variables for GraphQL query
    variables = {"cursor": cursor, "start": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "end": end_date.strftime("%Y-%m-%dT%H:%M:%SZ")}

    # Send request to GitHub API
    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})

    # Check if request was successful
    if response.status_code != 200:
        print(f"Error fetching discussion threads. Status code: {response.status_code}")
        break

    # Parse response data
    data = response.json()

    # Count the number of discussions created within the specified date range
    for discussion in data['data']['repository']['discussions']['nodes']:
        created_at = datetime.datetime.strptime(discussion['createdAt'], '%Y-%m-%dT%H:%M:%SZ').date()
        if start_date <= created_at <= end_date:
            if discussion['category']['name'] != 'announcements':  # exclude announcement category
                discussion_count += 1
                print(
                    f"Discussion created on {created_at} isLocked={discussion['locked']}")

                if discussion['locked']:
                    locked_discussion_count += 1

    # Check if there are more pages of data to fetch
    if data['data']['repository']['discussions']['pageInfo']['hasNextPage']:
        cursor = data['data']['repository']['discussions']['pageInfo']['endCursor']
    else:
        break

print(f"Number of discussions created between {start_date} and {end_date}: {discussion_count}")
print(f"Number of locked discussions (excluding announcements) created between {start_date} and {end_date}: {locked_discussion_count}")
