import requests
import json
import datetime
import configparser

class GithubBugAnalyzer:
    def __init__(self, config_file_path):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(config_file_path)
        self.name_of_community = self.config.get("community_name", "name")
        self.token_details = self.config.get("bearer", "token")
        self.bug_discussion = self.config.get("category", "bug_discussion")
        self.url = 'https://api.github.com/graphql'
        self.headers = {"Authorization": "bearer " + self.token_details}

    def get_bug_discussions(self):
        query = """
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
                    isAnswer
                    createdAt
                  }
                }
                createdAt
              }
            }
          }
        }
        """ % self.name_of_community

        has_next_page = True
        end_cursor = None
        bug_discussions = []

        while has_next_page:
            variables = {"cursor": end_cursor}
            response = requests.post(self.url, headers=self.headers, json={'query': query, 'variables': variables})

            if response.status_code == 200:
                json_data = json.loads(response.text)
                discussions = json_data["data"]["repository"]["discussions"]["nodes"]
                bug_discussions += [d for d in discussions if d["category"]["slug"] == self.bug_discussion]
                end_cursor = json_data["data"]["repository"]["discussions"]["pageInfo"]["endCursor"]
                has_next_page = json_data["data"]["repository"]["discussions"]["pageInfo"]["hasNextPage"]
            else:
                print("Request failed with status code:", response.status_code)
                break

        return bug_discussions

    def analyze_bug_response_time(self):
        bug_discussions = self.get_bug_discussions()

        num_bugs = len(bug_discussions)
        total_response_time = datetime.timedelta(0)

        for discussion in bug_discussions:
            bug_posted_time = datetime.datetime.strptime(discussion["createdAt"], '%Y-%m-%dT%H:%M:%SZ')

            if discussion["comments"]["totalCount"] > 0 and discussion["comments"]["nodes"][0]["isAnswer"]:
                first_response_time = datetime.datetime.strptime(discussion["comments"]["nodes"][0]["createdAt"],
                                                                 '%Y-%m-%dT%H:%M:%SZ')
                response_time = first_response_time - bug_posted_time
                total_response_time += response_time

        if num_bugs > 0:
            avg_response_time = total_response_time / num_bugs
            avg_response_time_hours = avg_response_time.total_seconds() / 3600
            print(f"Average time to answer a bug for {num_bugs} bug discussions: {avg_response_time_hours:.2f} hours")
        else:
            print("No bug discussions found.")

if __name__ == '__main__':
    analyzer = GithubBugAnalyzer("config.ini")
    analyzer.analyze_bug_response_time()

