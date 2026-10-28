import requests 
import json
import wifi
import urequests

# Assemble the URL for the API call 
api_url = "https://cad.onshape.com/api/v17/assemblies/d/6a7f51e191a2177f3e4d21bc/w/8c9532c0822f87a540b45a77/e/355ef89134bd64ad749524db/matevalues"

# Optional query parameters can be assigned 
params = {}

# Use your keys
access_key = "on_HacWvWQ9Ouv5G7f4YZjdJ"
secret_key = "Isenw6qpfdE4lK5i69uGtTuLij6dvXXGrw7KFXXXhsw7NIkQ"

# Define the header for the request 
headers = {'Accept': 'application/json;charset=UTF-8;qs=0.09',
           'Content-Type': 'application/json'}

def write_angle_servo1(angle_1):
    write_1 = {
      "mateValues": [
        {
          "featureId": "M50NE2oB/FMifCpro",
          "jsonType": "Revolute",
          "mateName": "Servo 1",
          "ownerOccurrencePath": [],
          "rotationZ": angle_1
        }
      ]
    }

    response = requests.post(api_url, json=write_1, auth=(access_key, secret_key),
                        headers=headers)

def write_angle_servo2(angle_2):
    write_2 = {
      "mateValues": [
        {
          "featureId": "MDbHWolkHDKkwaJIK",
          "jsonType": "Revolute",
          "mateName": "Servo 2",
          "ownerOccurrencePath": [],
          "rotationZ": angle_2
        }
      ]
    }

    response = requests.post(
            api_url, 
            json=write_2,
            auth=(access_key, secret_key),
            headers=headers
        )
    
    return response.json()

result = write_angle_servo2(60)
print(json.dumps(result, indent=4))