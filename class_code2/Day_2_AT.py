import urequests
import wifi

wifi.connect_wifi()

AIRTABLE_TOKEN = os.getenv("AIRTABLE_TOKEN")
url ="https://api.airtable.com/v0/appPEV50bLCHxnHUu/testtable"
headers = {'Authorization': 'Bearer ' + token}

response = urequests.get(url, headers=headers)

if (response.status_code == 200):
    print("Successful request")
else:
    print("Unsuccessful request")
    
print(response.json())




    

