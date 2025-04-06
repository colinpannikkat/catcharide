import requests

def test_endpoint(endpoint="/"):
    url = f"http://127.0.0.1:5000{endpoint}"
    response = requests.get(url)
    print(response.json())

test_endpoint("/")
test_endpoint("/status")