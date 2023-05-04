import csv
import requests

# Define the GraphQL query to get the schema information for the Discussion type
query = '''
{
  __type(name: "Discussion") {
    fields {
      name
      description
    }
  }
}
'''

# Set the GitHub API endpoint and authorization headers
url = 'https://api.github.com/graphql'
headers = {'Authorization': 'Bearer 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'}

# Execute the GraphQL query and save the schema information to a CSV file
response = requests.post(url, json={'query': query}, headers=headers)
data = response.json()['data']['__type']['fields']

with open('discussion_schema.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Name', 'Description'])
    for field in data:
        name = field['name']
        description = field['description']
        writer.writerow([name, description])

print('Discussion schema saved to discussion_schema.csv')
