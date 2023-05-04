import requests
import json
import datetime
import configparser

class first_responce_avg_time:
    def __init__(self, community_name, bearer_token, category):
        self.community_name = community_name
        self.bearer_token = bearer_token
        self.category = category
        
        # GraphQL query to retrieve the bug discussions and their first responses
        self.query = """
        query($cursor: String) {
          repository(owner: "%s", name: "community") {
            discussions(first: 100, after: $cursor) {
              pageInfo {
                endCursor
                hasNextPage
              }
              nodes {
                category {
                  slug
                }
                comments(first: 1) {
                  totalCount
                  nodes {
                    createdAt
                  }
                }
                createdAt
              }
            }
          }
        } 
        """ % self.community_name
        
        # Set up the GraphQL API endpoint and headers
        self.url = 'https://api.github.com/graphql'
        self.headers = {"Authorization": "bearer " + self.bearer_token}
        
        self.num_issues = 0
        self.total_response_time = datetime.timedelta(0)
        
    def get_bug_discussions(self):
        end_cursor = None
        has_next_page = True
        
        while has_next_page:
            variables = {"cursor": end_cursor} if end_cursor else {}
            response = requests.post(self.url, headers=self.headers, json={'query': self.query, 'variables': variables})
            
            if response.status_code == 200:
                json_data = json.loads(response.text)
                discussions = json_data["data"]["repository"]["discussions"]["nodes"]
                issue_discussions = [d for d in discussions if d["category"]["slug"] == self.category]
                self.num_issues += len(issue_discussions)

                for discussion in issue_discussions:
                    # Convert the createdAt timestamp to a datetime object
                    bug_posted_time = datetime.datetime.strptime(discussion["createdAt"], '%Y-%m-%dT%H:%M:%SZ')

                    # Calculate the time difference between the bug posted time and the first response time
                    if discussion["comments"]["totalCount"] > 0:
                        first_response_time = datetime.datetime.strptime(discussion["comments"]["nodes"][0]["createdAt"], '%Y-%m-%dT%H:%M:%SZ')
                        response_time = first_response_time - bug_posted_time
                        self.total_response_time += response_time

                end_cursor = json_data["data"]["repository"]["discussions"]["pageInfo"]["endCursor"]
                has_next_page = json_data["data"]["repository"]["discussions"]["pageInfo"]["hasNextPage"]
            else:
                print("Request failed with status code:", response.status_code)
                break

    def print_average_response_time(self):
        if self.num_issues > 0:
            avg_response_time = self.total_response_time / self.num_issues
            avg_response_time_hours = avg_response_time.total_seconds() / 3600
            print(f"Average time of first response for {self.num_issues} issues discussions: {avg_response_time_hours:.2f} hours")
        else:
            print("No bug discussions found.")
            
if __name__ == "__main__":
    config = configparser.ConfigParser(interpolation=None)
    config.read("config.ini")
    
    community_name = config.get("community_name", "name")
    bearer_token = config.get("bearer", "token")
    category = config.get("category", "bug_discussion")
    
    github_api = first_responce_avg_time(community_name, bearer_token, category)
    github_api.get_bug_discussions()
    github_api.print_average_response_time()

