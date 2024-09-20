import json
import requests
import argparse
from pathlib import Path
from pymisp import PyMISP, MISPObject, MISPAttribute
from urllib3.exceptions import InsecureRequestWarning
from keys import misp_url, misp_key, misp_verifycert
from ctfd_config import ctfd_url, ctfd_token

# Suppress the warnings from urllib3 (optional)
#requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def fetch_data_from_ctfd(challenge_id):
    # sample ctfd_url for reference = "https://demo.ctfd.io/api/v1/challenges/"+str(challenge_id)
    ctfd_api_url = ctfd_url+"/api/v1/challenges/"+str(challenge_id)
    headers = {
        "Authorization": "Token "+ctfd_token,
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(ctfd_api_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        challenge_data = data['data']
        return challenge_data
        
    except requests.exceptions.RequestException as e:
        # Handle different error types (e.g., ConnectionError, HTTPError)
        print(f"Error retrieving data for challenge ID: {challenge_id} - {e}")
        return None
        
def upload_ctfd_data_to_misp(challenge_data, event_id, comment):
    try:
        misp = PyMISP(misp_url, misp_key, misp_verifycert)
        ctf_object = MISPObject(name="ctf-challenge")
    except Exception as error:
        print(f"Error connecting to MISP: {error}")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with MISP: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    else:
        ctf_object = MISPObject(name="ctf-challenge")

        ctf_object.comment = comment if args.comment != None else None
        ctf_object.add_attribute("title", type='text', value=challenge_data['name'])
        ctf_object.add_attribute("category", type='text', value=challenge_data['category'])
        if(challenge_data['description']):
            ctf_object.add_attribute("description", type='text', value=challenge_data['description'])
        ctf_object.add_attribute("points", type='float', value=challenge_data['value'])
        ctf_object.add_attribute("max_attempts", type='counter', value=challenge_data['max_attempts'])
        ctf_object.add_attribute("solves", type='counter', value=challenge_data['solves'])
        
        ## actual hints not included in json data - requires user interaction to agree to unlock hints
        ctf_object.add_attribute("hints", type='text', value=challenge_data['hints'])
        
        file_paths = challenge_data['files']
        
        # Download the file from the URL as a binary response
        for each_file in file_paths:
            # sample file_url for reference = "https://demo.ctfd.io"+each_file
            file_url = ctfd_url+each_file

            # Fixed: /files/{md5 hash}/{file_name} format
            file_name = each_file[40:each_file.find('?')]
            file_response = requests.get(file_url, stream=True)
            
            # Create a temporary file-like object using `Path.open()`
            with Path(file_name).open("wb") as temp_file:
                for chunk in file_response.iter_content(chunk_size=1024):
                    temp_file.write(chunk)
                temp_file_path = Path(file_name)
                ctf_object.add_attribute("attachment",value=temp_file_path.name, data=temp_file_path)
                
            # Delete file(s)
            temp_file_path.unlink()
        event = misp.add_object(event_id, ctf_object, pythonify=True)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script to populate data from CTF (that uses CTFd platform) into MISP using ctf-challenge MISP object')
    parser.add_argument("-e", "--event", required=True, help="The MISP Event ID where the CTF data will be added.")
    parser.add_argument("-c", "--comment", required=False, default=None, help="An optional comment or context to add to the 'ctf-challenge' MISP object.")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-sc", "--singlechallenge", required=False, help="Populate a single CTF challenge with the provided challenge ID.")
    group.add_argument("-m", "--max", required=False, help="Set the maximum challenge ID to process.")
    
    args = parser.parse_args()

    
    if(args.singlechallenge):
        challenge_data = fetch_data_from_ctfd(args.singlechallenge)
        if(challenge_data):
            print(f"Challenge ID: {args.singlechallenge} - Challenge name: {challenge_data['name']}")
            upload_ctfd_data_to_misp(challenge_data, args.event, args.comment)
    else:               
        for challenge_id in range(1,int(args.max)+1):
            challenge_data = fetch_data_from_ctfd(challenge_id)
            if(challenge_data):
                print(f"Challenge ID: {challenge_id} - Challenge name: {challenge_data['name']}")
                upload_ctfd_data_to_misp(challenge_data, args.event, args.comment)