import requests
import json
from datetime import datetime
import configparser


class avg_time:
    def __init__(self):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read("config.ini")
        self.name_of_community = self.config.get("community_name", "name")
        self.token_details = self.config.get("bearer", "token")
        self.url = 'https://api.github.com/graphql'
        self.headers = {"Authorization": "bearer " + self.token_details}

    def run_query(self, query, variables=None):
        response = requests.post(self.url, headers=self.headers, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print("Request failed with status code:", response.status_code)
            return None

    def get_discussions(self):
        query = """
            query ($cursor: String) {
              repository(owner: "%s", name: "community") {
                discussions(first: 100, after: $cursor) {
                  pageInfo {
                    hasNextPage
                    endCursor
                  }
                  nodes {
                    id
                    createdAt
                    comments(first: 1) {
                      nodes {
                        createdAt
                      }
                    }
                  }
                }
              }
            }
            """ % self.name_of_community

        cursor = None
        count = 0
        total_response_time = 0

        while True:
            
            variables = {'cursor': cursor}
            json_data = self.run_query(query, variables)
            if json_data is not None:
                discussions = json_data["data"]["repository"]["discussions"]["nodes"]
                for d in discussions:
                    if d["comments"]["nodes"]:
                        posted_time = datetime.strptime(d["createdAt"], '%Y-%m-%dT%H:%M:%SZ')
                        response_time = datetime.strptime(d["comments"]["nodes"][0]["createdAt"], '%Y-%m-%dT%H:%M:%SZ')
                        total_response_time += (response_time - posted_time).total_seconds()
                        count += 1
                has_next_page = json_data["data"]["repository"]["discussions"]["pageInfo"]["hasNextPage"]
                if has_next_page:
                    cursor = json_data["data"]["repository"]["discussions"]["pageInfo"]["endCursor"]
                else:
                    break
            else:
                break

        if count > 0:
            avg_response_time = total_response_time / count / 3600
            print(f"Average time of first response: {avg_response_time:.2f} hours")
        else:
            print("No discussions with comments found.")
if __name__ == '__main__':
    api = avg_time()
    api.get_discussions()

