import requests
import json

# Test the form link generation endpoint directly
try:
    response = requests.post('http://localhost:5000/generate-form-link/43', 
                           headers={'Content-Type': 'application/json'})
    print('Status Code:', response.status_code)
    print('Response:', response.json())
except Exception as e:
    print('Error:', e)
