from bs4 import BeautifulSoup
import json
import requests


def parse_html(html_file):
    html = open("labs.html", encoding="utf-8").read()  # replace with your file path

    soup = BeautifulSoup(html, "html.parser")

    labs_by_topic = {}
    current_topic = None

    for tag in soup.find_all(["h2", "div"]):
        if tag.name == "h2":
            current_topic = tag.get_text(strip=True)
            labs_by_topic[current_topic] = []
        elif tag.name == "div" and "widgetcontainer-lab-link" in tag.get("class", []):
            lab_info = {
                "difficulty": tag.find("span", class_=["label-light-green-small",
                                                       "label-light-blue-small",
                                                       "label-purple-small"]).get_text(strip=True),
                "title": tag.find("a").get_text(strip=True),
                "url": tag.find("a")["href"],
                "status": tag.find("span", class_="lab-status-icon").get_text(strip=True)
            }
            labs_by_topic[current_topic].append(lab_info)

    with open("labs_by_topic.json", "w", encoding="utf-8") as f:
        json.dump(labs_by_topic, f, indent=4, ensure_ascii=False)



def create_column(column_name):
    url = f"{JIRA_DOMAIN}/jsw2/graphql?operation=SoftwareColumnCreate"

    headers = {
        "Accept": "application/json,text/javascript,*/*",
        "Content-Type": "application/json",
    }

    payload = {
        "operationName": "SoftwareColumnCreate",
        "query": """mutation SoftwareColumnCreate($boardId: ID!, $columnName: String!){
            createColumn(input: {boardId: $boardId, columnName: $columnName}) {
                newColumn {
                    id
                    name
                    maxIssueCount
                    status { id name }
                    columnStatus {
                        status { id name category }
                    }
                    isInitial
                    isDone
                    transitionId
                }
            }
        }""",
        "variables": {
            "boardId": "2",
            "columnName": str(column_name)
        }
    }

    resp = requests.post(
        url,
        headers=headers,
        auth=(EMAIL, API_TOKEN),
        data=json.dumps(payload)
    )
    return resp.json().get("data").get("createColumn").get("newColumn").get("transitionId")



def add_ticket(auth_, title, url, user_id):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = json.dumps({
        "fields": {
            "project": {
                "key": PROJECT_KEY
            },
            "summary": str(title),
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": str("https://portswigger.net"+url)
                            }
                        ]
                    }
                ]
            },
            "issuetype": {"name": "Task"},
            "assignee": {"id": str(user_id)},
        }
    })

    url = f"{JIRA_DOMAIN}/rest/api/3/issue"
    response = requests.post(url, data=payload, headers=headers, auth=auth_)

    if response.status_code == 201:
        return str(response.json().get("key"))
    else:
        print("Failed:", response.status_code, response.text)
        return {}

def move_issue_to_column(auth_, issue_key, transition_id):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    transition_url = f"{JIRA_DOMAIN}/rest/api/3/issue/{issue_key}/transitions"
    payload = {"transition": {"id": str(transition_id)}}

    resp = requests.post(transition_url, headers=headers, auth=auth_, json=payload)

    if resp.status_code == 204:
        print(f"✅ Issue {issue_key} moved using transition {transition_id}")
    else:
        print("❌ Failed:", resp.status_code, resp.text)



if __name__ == "__main__":
    JIRA_DOMAIN = ""
    EMAIL = ""
    API_TOKEN = ""
    PROJECT_KEY = ""
    USER_ID = ""

    with open("labs_by_topic.json", "r+") as fd:
        data = json.load(fd)
        auth = (EMAIL, API_TOKEN)
        for key, value in data.items():
            column_id = create_column(key)
            print(column_id)
            for lab in value:
                try:
                    title = f"{lab.get('difficulty')}: {lab.get('title')}"
                    ticket_id = add_ticket(auth, title, lab.get("url"), USER_ID)
                    print(ticket_id)
                    move_issue_to_column(auth, ticket_id, column_id)
                except Exception as e:
                    print(e)



