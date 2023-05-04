import json
import requests
import configparser

class total_count:
    def __init__(self, community_name, token):
        self.community_name = community_name
        self.token = token
        self.url = 'https://api.github.com/graphql'
        self.headers = {"Authorization": "Bearer " + self.token}

    def query(self, query, variables=None):
        response = requests.post(self.url, headers=self.headers, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            return json.loads(response.text)["data"]
        else:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

    def get_discussion_count_by_category(self):
        query = """
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
        
        has_next_page = True
        end_cursor = None
        category_counts = {}
        discussions_seen = set()

        while has_next_page:
            variables = {"cursor": end_cursor}
            response_data = self.query(query, variables)
            discussions = response_data["repository"]["discussions"]
            end_cursor = discussions["pageInfo"]["endCursor"]
            has_next_page = discussions["pageInfo"]["hasNextPage"]
            for discussion in discussions["nodes"]:
                category_slug = discussion["category"]["slug"]
                if category_slug == "announcements":
                    continue  # Skip this discussion if it's in the "announcements" category
                if category_slug not in category_counts:
                    category_counts[category_slug] = 0
                if discussion["id"] not in discussions_seen:
                    category_counts[category_slug] += 1
                    discussions_seen.add(discussion["id"])

        total_count = sum(category_counts.values())
        print(f"Total discussion count: {total_count}")

        
if __name__ == "__main__":
    config = configparser.ConfigParser(interpolation=None)
    config.read("config.ini")
    name_of_community = config.get("community_name", "name")
    token_details = config.get("bearer", "token")
    api = total_count(name_of_community, token_details)
    api.get_discussion_count_by_category()

