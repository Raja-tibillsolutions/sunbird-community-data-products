import json
import requests
import configparser


class total_count_exculding_announcement:
    def __init__(self, token_details, name_of_community):
        self.url = 'https://api.github.com/graphql'
        self.headers = {"Authorization": "Bearer " + token_details}
        self.name_of_community = name_of_community

    def _send_query(self, query, variables):
        response = requests.post(self.url, headers=self.headers, json={'query': query, 'variables': variables})

        if response.status_code != 200:
            raise ValueError(f'Request failed with status code: {response.status_code}')

        return json.loads(response.text)

    def get_discussion_counts_by_category(self):
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
        """ % self.name_of_community

        has_next_page = True
        end_cursor = None
        category_counts = {}
        discussions_seen = set()

        while has_next_page:
            variables = {"cursor": end_cursor}
            data = self._send_query(query, variables)

            discussions = data["data"]["repository"]["discussions"]
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

        return category_counts


if __name__ == '__main__':
    config = configparser.ConfigParser(interpolation=None)
    config.read("config.ini")

    name_of_community = config.get("community_name", "name")
    token_details = config.get("bearer", "token")

    api = total_count_exculding_announcement(token_details, name_of_community)
    category_counts = api.get_discussion_counts_by_category()

    total_count = sum(category_counts.values())
    print(f"Total discussion count excluding announcements: {total_count}")


