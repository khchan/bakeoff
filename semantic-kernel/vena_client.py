import requests
import base64
import os

def get_header(venaUser, venaKey):
    token = base64.b64encode(f'{venaUser}:{venaKey}'.encode()).decode()
    return {
        'Authorization': f'VenaBasic {token}',
        'Content-Type': 'application/json'
    }
    
def list_models() -> str:
    header = get_header(os.environ.get("VENA_USER"), os.environ.get("VENA_KEY"))
    response = requests.get(
        f'{os.environ.get("VENA_ENDPOINT")}/api/models/withDimensions',
        headers=header
    )
    if response.status_code != 200:
        raise Exception(f"Error: Received status code {response.status_code}. Message: {response.text}")
    
    data = response.json()
    return [
        {
            "id": model['id'],
            "name": model['name'],
            "description": model['desc']
        }
        for model in data
    ]

def get_model(id: int) -> str:
    header = get_header(os.environ.get("VENA_USER"), os.environ.get("VENA_KEY"))
    response = requests.get(
        f'{os.environ.get("VENA_ENDPOINT")}/api/models/{id}/dimensions?incMembers=false&incAttributes=false',
        headers=header
    )
    if response.status_code != 200:
        raise Exception(f"Error: Received status code {response.status_code}. Message: {response.text}")
    
    data = response.json()
    return [
        {
            "id": dimension['id'],
            "number": dimension['number'],
            "name": dimension['name'],
            "typeDefinition": dimension['typeDefinition']
        }
        for dimension in data
    ]
    
def get_children_of_member(model_id: int, dimension_number: int, member_id: str) -> str:
    url = f'{os.environ.get("VENA_ENDPOINT")}/api/models/{model_id}/dimensions/{dimension_number}/members/{member_id}/children'
    header = get_header(os.environ.get("VENA_USER"), os.environ.get("VENA_KEY"))
    response = requests.get(
        url,
        headers=header
    )
    if response.status_code != 200:
        raise Exception(f"Error: Received status code {response.status_code}. Message: {response.text}")
    
    data = response.json()
    return [
        {
            "id": member['id'],
            "name": member['name'],
            "alias": member['alias'],
            "numChildren": member['numChildren']
        }
        for member in data
    ]
    
def search_members(model_id: int, dimension_id: int, query: str) -> str:
    header = get_header(os.environ.get("VENA_USER"), os.environ.get("VENA_KEY"))
    response = requests.post(
        f'{os.environ.get("VENA_ENDPOINT")}/api/search/suggestions',
        headers=header,
        json=[
            {"name":query,"alias":query,"dimensionId":dimension_id,"modelId":model_id,"limit":500,"type":"MEMBER"},
            {"name":query,"dimensionId":dimension_id,"modelId":model_id,"limit":500,"type":"ATTRIBUTE"}
        ]
    )
    if response.status_code != 200:
        raise Exception(f"Error: Received status code {response.status_code}. Message: {response.text}")
    
    return response.json()
