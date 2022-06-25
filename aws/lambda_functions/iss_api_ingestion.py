from cmath import e
from wsgiref.validate import validator
import boto3
from io import BytesIO
import json
import jsonschema
import requests
from yaml import load

def download_satellite_data(norad_id: int = 25544, units: str = "miles", is_tle:bool = False) -> dict:
    '''_summary_

    Parameters
    ----------
    norad_id : int, optional
        _description_, by default 25544. This is the NORAD ID for the ISS.

    units : str, optional
        _description_,
         by default "miles". Can alternativly be 'kilometers'.

    is_tle : bool, optional
        _description_,
        by default False. TLE data is used for plotting the orbit.
        When this parameter is False we instead return positioning data (lat, long, altitude, etc..)
    '''

    # If we want to return positioning data
    if not is_tle:
        # Get position data from API
        api_url = f'https://api.wheretheiss.at/v1/satellites/{norad_id}?units={units}&?timestamp'
        iss_data = requests.get(api_url).json()
        iss_data['source'] = 'https://wheretheiss.at/'
        iss_data['checking'] = 'faslseeeee'

    # If we want to return orbital data
    elif is_tle:
        # Get tle data from API
        api_url_tle = f'https://api.wheretheiss.at/v1/satellites/{norad_id}/tles'
        iss_data = requests.get(api_url_tle).json()
        iss_data['source'] = 'https://wheretheiss.at/'
        
    return iss_data

def iss_data_validation(schema:dict, json_to_validate:dict) -> bool:
    '''_summary_

    Parameters
    ----------
    schema : dict
        _description_
        Json schema used to validate against
    json_to_validate : dict
        _description_
        Json used to validate against the schema

    Returns
    -------
    bool
        _description_
        returns True if json is valid and False if not valid
    '''

    # Validate Schema
    schema_validator = jsonschema.Draft202012Validator(schema)

    # Using the above schema, check if our json is valid
    is_valid_json = schema_validator.is_valid(instance=json_to_validate)

    return is_valid_json

def upload_to_s3(data:dict, bucket_name:str, key:str):
    '''_summary_
    Upload fileobject to desired s3 bucket.

    Parameters
    ----------
    data : dict
        _description_
        data to be uploaded. In our case this is
        most likely a json API response.
    bucket_name : str
        _description_
        Desired bucket location to put the fileobj
    key : str
        _description_
        path/name of fileobject. Example (path/filename.json)
    '''

    # Create s3 client
    s3 = boto3.client('s3')
    
    # Write data to json object
    data_as_json_object = json.dumps(data).encode('utf-8')   

    # Write to IO buffer
    fileobj = BytesIO(data_as_json_object)

    s3.upload_fileobj(fileobj, bucket_name, key)
