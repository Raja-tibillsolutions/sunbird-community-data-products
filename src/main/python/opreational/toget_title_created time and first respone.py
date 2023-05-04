import csv
import requests

# Define the GraphQL query with a cursor parameter for pagination
query = """
query($cursor: String) {
  repository(owner: "sunbird-lern", name: "community") {
    discussions(first: 100, after: $cursor) {
      totalCount
      pageInfo {
        endCursor
        hasNextPage
      }
      nodes {
        title
        createdAt
        comments(first: 1) {
          nodes {
            author {
              login
            }
            createdAt
            body
          }
        }
      }
    }
  }
}
"""

# Set the GitHub API endpoint and authorization headers
url = 'https://api.github.com/graphql'
headers = {'Authorization': 'Bearer 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'}

# Execute the GraphQL query with pagination
end_cursor = None
data = []
while True:
    variables = {'cursor': end_cursor} if end_cursor else {}
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    response_data = response.json()['data']['repository']['discussions']
    data += response_data['nodes']
    if not response_data['pageInfo']['hasNextPage']:
        break
    end_cursor = response_data['pageInfo']['endCursor']

# Write the data to a CSV file
with open('discussions.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Created At', 'First Response Author', 'First Response Created At', 'First Response Body'])
    for discussion in data:
        title = discussion['title']
        created_at = discussion['createdAt']
        if discussion['comments']['nodes']:
            first_response_author = discussion['comments']['nodes'][0]['author']['login']
            first_response_created_at = discussion['comments']['nodes'][0]['createdAt']
            first_response_body = discussion['comments']['nodes'][0]['body']
        else:
            first_response_author = ''
            first_response_created_at = ''
            first_response_body = ''
        writer.writerow([title, created_at, first_response_author, first_response_created_at, first_response_body])

print('Data saved to discussions.csv')


