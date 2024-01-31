import requests

# API endpoint for storing parking space information
api_url = "http://loadbalancer-248870272.eu-west-3.elb.amazonaws.com:8080/api/ai/availableParkingSpots"


def data(parking_spaces):
    counter = 0
    for parkingspace in parking_spaces:
        if parkingspace.status == "occupied":
            counter += 1

    data = {
        "total": len(parking_spaces),
        "occupied": counter
    }

    response = requests.put(api_url, json=data)
    if response.status_code == 200:
        print(f"Successfully stored pinformation.")
    else:
        print(f"Failed to store parking spaceinformation. Status Code: {response.status_code}")
