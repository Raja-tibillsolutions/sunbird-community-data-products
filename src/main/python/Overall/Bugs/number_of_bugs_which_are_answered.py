import requests
import json
import configparser

class get_answered_bugs:
    def __init__(self):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read("config.ini")
        self.name_of_community = self.config.get("community_name", "name")
        self.token_details = self.config.get("bearer", "token")
        self.bug_discussion= self.config.get("category","bug_discussion")

    def get_discussions(self, page_cursor=None):
        query = """
        query($cursor: String) {
          repository(owner: "%s", name: "community") {
            discussions(first: 100, after: $cursor) {
              totalCount
              pageInfo {
                hasNextPage
                endCursor
              }
              nodes {
                id
                category {
                  slug
                }
                comments(first: 1) {
                  totalCount
                  nodes{
                    isAnswer
                  }
                }
              }
            }
          }
        }
        """ % self.name_of_community

        url = 'https://api.github.com/graphql'
        headers = {"Authorization": "bearer " + self.token_details}
        variables = {'cursor': page_cursor}
        response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})

        if response.status_code == 200:
            json_data = json.loads(response.text)
            discussions = json_data["data"]["repository"]["discussions"]
            nodes = discussions["nodes"]
            has_next_page = discussions["pageInfo"]["hasNextPage"]
            end_cursor = discussions["pageInfo"]["endCursor"]
            if page_cursor is not None:
                nodes = self.filter_duplicate_discussions(nodes)
            if has_next_page:
                next_nodes, next_end_cursor = self.get_discussions(end_cursor)
                nodes.extend(next_nodes)
                end_cursor = next_end_cursor
            return nodes, end_cursor
        else:
            raise Exception("Request failed with status code:", response.status_code)

    def filter_duplicate_discussions(self, discussions):
        ids = set()
        filtered_discussions = []
        for discussion in discussions:
            if discussion["id"] not in ids:
                ids.add(discussion["id"])
                filtered_discussions.append(discussion)
        return filtered_discussions

    def get_answered_bugs(self):
        nodes, end_cursor = self.get_discussions()
        bug_discussions = [d for d in nodes if d["category"]["slug"] == self.bug_discussion]
        answered_bugs = [d for d in bug_discussions if d["comments"]["totalCount"] > 0]
        num_answered_bugs = len(answered_bugs)
        return answered_bugs, num_answered_bugs

if __name__ == "__main__":
    api = get_answered_bugs()
    answered_bugs, num_answered_bugs = api.get_answered_bugs()
    print("Number of answered bugs:", num_answered_bugs)

