"""

import requests

# Your Zenodo API token
ACCESS_TOKEN = 'your_api_token_here'

# Zenodo deposition endpoint
DEPOSITION_URL = 'https://zenodo.org/api/deposit/depositions'

# Path to your zip file
ZIP_FILE_PATH = 'path/to/your/file.zip'

# Prepare the metadata for your deposition
metadata = {
    'title': 'Your Dataset Title',
    'upload_type': 'dataset',
    'access_right': 'restricted',
    'license': 'your_license',
    'description': 'Your dataset description.',
}

# Create a new deposition
headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {ACCESS_TOKEN}'}
response = requests.post(DEPOSITION_URL, json={}, headers=headers)

if response.status_code == 201:
    deposition_id = response.json()['id']
    print(f'Deposition created with ID: {deposition_id}')

    # Upload the zip file to the deposition
    files = {'file': open(ZIP_FILE_PATH, 'rb')}
    upload_url = f'{DEPOSITION_URL}/{deposition_id}/files'
    response = requests.post(upload_url, files=files, headers=headers)

    if response.status_code == 201:
        print('File uploaded successfully.')

        # Publish the deposition to make it publicly accessible
        publish_url = f'{DEPOSITION_URL}/{deposition_id}/actions/publish'
        response = requests.post(publish_url, json={}, headers=headers)

        if response.status_code == 202:
            print('Deposition published successfully.')
        else:
            print(f'Error publishing deposition: {response.text}')
    else:
        print(f'Error uploading file: {response.text}')
else:
    print(f'Error creating deposition: {response.text}')

"""