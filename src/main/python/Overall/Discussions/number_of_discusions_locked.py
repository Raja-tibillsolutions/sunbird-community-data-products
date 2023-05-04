import requests
import json
import configparser


class locked_count:
    def __init__(self):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read("config.ini")
        self.name_of_community = self.config.get("community_name", "name")
        self.token_details = self.config.get("bearer", "token")
        self.headers = {"Authorization": "bearer " + self.token_details}
        self.url = 'https://api.github.com/graphql'

    def get_locked_discussion_count(self):
        query = """
        query ($cursor: String) {
          repository(owner: "%s", name: "community") {
            discussions(first: 100, after: $cursor) {
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                locked
              }
            }
          }
        }
        """ % self.name_of_community

        cursor = None
        count = 0

        while True:
            variables = {'cursor': cursor}
            response = requests.post(self.url, headers=self.headers, json={'query': query, 'variables': variables})
            if response.status_code == 200:
                json_data = json.loads(response.text)
                discussions = json_data["data"]["repository"]["discussions"]["nodes"]
                count += len([d for d in discussions if d["locked"] is True])
                has_next_page = json_data["data"]["repository"]["discussions"]["pageInfo"]["hasNextPage"]
                if has_next_page:
                    cursor = json_data["data"]["repository"]["discussions"]["pageInfo"]["endCursor"]
                else:
                    break
            else:
                print("Request failed with status code:", response.status_code)
                break

        return count


if __name__ == '__main__':
    api = locked_count()
    locked_discussion_count = api.get_locked_discussion_count()
    print(f"Total count of locked discussions: {locked_discussion_count}")

