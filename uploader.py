from typing import Final
from filestack import Client, Filelink

F_APIKEY: Final = 'AKfjUTTXNQMeeuQApU66yz'
F_SECURITY_KEY = 'U36TB7A3KJGEXMPTJ2AIH6QHDU'

def upload(path: str) -> str:
    """This Method takes in a file and returns a url to the file
    It Will be uploaded to the Filestack Servers"""
    client = Client(F_APIKEY)
    
    store_params = {
        "mimetype": "audio/mpeg"
    }

    new_filelink = client.upload(filepath=path, store_params=store_params)

    return new_filelink.url

def delete_file(url):
    client = Client(F_APIKEY)
    new_filelink = Filelink(client)
    response = new_filelink.delete(F_APIKEY, security=F_SECURITY_KEY)
    return response
