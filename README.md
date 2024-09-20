# ctfd-to-misp
This Python script fetches CTF challenge data from a CTFd platform and uploads it to a MISP instance as a custom MISP object (ctf-challenge).

## Requirements:

- Python 3.x
- requests
- pymisp
- urllib3
- MISP instance with uploaded ctf-challenge MISP object.

## Installation:
Recommended to use Python Virtual Environment (Refer [here](https://docs.python.org/3/tutorial/venv.html))

1. Install the required libraries using pip: 
```pip install requests pymisp urllib3```

2. Edit keys.py and ctfd_config.py file with your CTFd and MISP credentials.
3. Ensure your MISP instance is running with ctf-challenge (custom MISP object) uploaded at
```
/var/www/MISP/app/files/misp-objects/objects/ctf-challenge/definition.json
```
> You may refer steps detailed out in [here](https://www.misp-project.org/2021/03/17/MISP-Objects-101.html/) to upload the ctf-challenge MISP object.
4. Ensure in your Python pymisp library folder contains the custom MISP object - ctf-challenge
```
If you running it directly, 
C:\Users\yourmachine_hostname\AppData\Local\Programs\Python\Python312\Lib\site-packages\pymisp\data\misp-objects\objects

If you are using Python Virtual Environment (recommended)
...your_virtual_env\Lib\site-packages\pymisp\data\misp-objects\objects\ctf-challenge\definition.json
```


## Usage:
```python ctfd_to_misp.py -e <MISP_EVENT_ID> -sc <CTFD_CHALLENGE_ID>``` \
or \
```python ctfd_to_misp.py -e <MISP_EVENT_ID> -m <MAX_CHALLENGE_ID>```

## Arguments:
```
-e or --event: The MISP event ID where the CTF data will be added.
-sc or --singlechallenge: The CTF challenge ID to fetch and upload.
-m or --max: The maximum challenge ID to process.
```

## Example:
```python ctfd_to_misp.py -e 12345 -sc 20```

This will fetch challenge data for CTF challenge ID 20 and upload it to MISP event 12345.

```python ctfd_to_misp.py -e 12345 -m 10```

This will fetch challenge data for CTF challenge ID 1 until 10 and upload it to MISP event 12345.

## Additional Notes:
- The script currently handles basic CTF challenge data such as name, category, description, points, max attempts, solves, and files.
- You may need to adjust the code to handle specific CTFd or MISP configurations.