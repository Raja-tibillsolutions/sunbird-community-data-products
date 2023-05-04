import json
import requests
import configparser


class total_bugs:
    def __init__(self, community_name, token, category):
        self.community_name = community_name
        self.token = token
        self.category = category
        self.query = """
        query($cursor: String) {
          repository(owner: "%s", name: "community") {
            discussions(first: 100, after: $cursor) {
              pageInfo {
                endCursor
                hasNextPage
              }
              nodes {
                id
                category {
                  slug
                }
              }
            }
          }
        }
        """ % self.community_name

    def get_bug_discussions(self):
        url = 'https://api.github.com/graphql'
        headers = {"Authorization": "bearer " + self.token}

        has_next_page = True
        end_cursor = None
        num_bugs = 0
        discussions_seen = set()

        while has_next_page:
            variables = {"cursor": end_cursor}
            response = requests.post(url, headers=headers, json={'query': self.query, 'variables': variables})

            if response.status_code == 200:
                json_data = json.loads(response.text)
                discussions = json_data["data"]["repository"]["discussions"]
                end_cursor = discussions["pageInfo"]["endCursor"]
                has_next_page = discussions["pageInfo"]["hasNextPage"]
                bug_discussions = [d for d in discussions["nodes"] if d["category"]["slug"] == self.category and d["id"] not in discussions_seen]

                num_bugs += len(bug_discussions)
                discussions_seen.update(d["id"] for d in bug_discussions)
            else:
                print("Request failed with status code:", response.status_code)
                break

        return num_bugs


if __name__ == '__main__':
    config = configparser.ConfigParser(interpolation=None)
    config.read("config.ini")

    name_of_community = config.get("community_name", "name")
    token_details = config.get("bearer", "token")
    bug_discussion = config.get("category", "bug_discussion")

    api = total_bugs(name_of_community, token_details, bug_discussion)
    num_bugs = api.get_bug_discussions()

    print("Total number of bugs:", num_bugs)

