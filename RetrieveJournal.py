import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import pdb
import json

# Load environment variables from the .env file
load_dotenv('Journal.env')

# Access the Notion API key and Database ID from environment variables
NOTION_API_KEY = os.getenv('NOTION_KEY')
DATABASE_ID = os.getenv('NOTION_PAGE_ID')
ACCOUNTS_ID = os.getenv('NOTION_ACCTS_ID')
NOTION_VERSION = '2022-06-28'

with open('accounts.json', 'rb') as accts_file:
    # To DO: Error Handling
    ACCTS = json.load(accts_file)
    
# Set up the headers for authentication and Notion API version
headers = {
    "Authorization": f'Bearer {NOTION_API_KEY}',
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

# Define the database endpoint URL
def get_accounts(filter_obj=None):
    acct_url = f"https://api.notion.com/v1/databases/{ACCOUNTS_ID}/query"
    # Make the POST request to filter
    response = requests.post(acct_url, headers=headers, json=filter_obj)
    # List comprehension version:
    #titles = [item["properties"]["Name"]['title'] for item in response.json()['results']]
    #titles= [title[0]['text']['content'] for title in titles]

    # Loop Version of above list comprehension:
    titles = []
    for item in response.json()['results']:
        title_obj = item["properties"]["Name"]['title']
        acct_id = item['id']
        title = title_obj[0]['text']['content']
        titles.append((title, acct_id))
    titles = dict(titles)
    #print(response.json()['results'][]["properties"]["Group"])
    #print(response.json().keys())
    return titles

# Define the function to add a new row (create a new page) to the Journal Entries database
# ?KSD? Can the status parm be defaulted to "Test" if not passed?  See get_accounts(filter_obj=None) call above
def create_page_in_notion(name, status, amount, action, note, date, from_acct, to_acct):
    url = "https://api.notion.com/v1/pages"

# To Do:  Error handling if either Key (from_acct/to_acct) is not found, then refresh ACCTS, then retry search
    from_acct = ACCTS[from_acct]
    to_acct= ACCTS[to_acct]

    # Define the page data, mapping your input parameters to the database properties
    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Name": {
                "title": [
                    {
                        "type": "text",
                        "text": {"content": name}
                    }
                ]
            },
            "Status": {
                "select": {"name": "Test"}
            },
            "Amount": {
                "number": amount
            },
            "Action": {
                "select": {"name": action}
            },
            "Note": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": note}
                    }
                ]
            },
            "Date*": {
                "date": {"start": date}
            },
            "From Account": {
                "relation": [
                    {
                        "id": from_acct
                    }  # Relation to the "From Account" page
                ]
            },
            "To Account": {
                "relation": [
                    {
                        "id": to_acct
                    }  # Relation to the "To Account" page
                ]
            }
        }
    }

    # Make the POST request to create a new page
    response = requests.post(url, headers=headers, json=data)

    # Check if the request was successful
    if response.status_code == 200:
        print("Page created successfully.")
        print(response.json()["id"])
        pg_id = response.json()["id"]
        dateobj = datetime.strptime(date, '%Y-%m-%d')
        fdate = dateobj.strftime('%b%y')
        ud_title = "We updated this title"

        # Create a meaningful and unique Title (aka Name) from other values in the Notion database row:
        # 1) Assemble the ID prefix and ID given by Notion which ensures uniqueness in this database.
        je_id = response.json()["properties"]["ID"]["unique_id"]["prefix"] + "-" + str(response.json()["properties"]["ID"]["unique_id"]["number"])
        # 2)  Concatenate and format the selected row values which give the Title (Name) meaning to the user.
        je_id += f': {name} {fdate}'

        data = {
            "properties": {
                "Name": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": je_id}
                        }
                    ]
                }
            }
        }
        pg_url = f'https://api.notion.com/v1/pages/{pg_id}'
        print(pg_url)
        pg_headers = {
            "Authorization": f'Bearer {NOTION_API_KEY}',
            "Notion-Version": NOTION_VERSION
        }
        pg_response = requests.patch(pg_url, headers=pg_headers, json=data)
        if pg_response.status_code == 200:
            print(pg_response.text)
        else:
            print(f"Error: {pg_response.status_code}")
            print(pg_response.text)

        print(response.text)
        return response.json()["id"]
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

# Example usage
        #if __name__ == "__main__":
        #create_page_in_notion(
        #name="Test",
        #amount=150.00,
        #action="Deposit to",
        #note="Sample note for this entry.",
        #date="2024-10-15",
        #toAcct = '110adc52e15880fd98e1c49131ec35a3',
        #fromAcct = 'b0ed7534d01345dd84f8dc0518b87b20',
        #status = "Test"
        #)

if __name__ == "__main__":
    filter_obj = {
        "filter": {
            "property": "Group",
            "select": {
                "equals": "Credit Card"
            }
        }
    }
    print( get_accounts() )
    




