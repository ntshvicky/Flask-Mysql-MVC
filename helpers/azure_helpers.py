import base64
from azure.storage.blob import BlobClient, ContainerClient


ACCOUNT_URL = "https://youraccount.blob.core.windows.net"
CONNECTION_STRING = "Your connection string"
CONTAINER_NAME = "container_name"

def returnBasePath():
    return "{}/{}".format(ACCOUNT_URL, CONTAINER_NAME)

# upload file from given path
# file_path - file path - string
# object_name - file_path in s3 bucket - string
def upload_file_input(input_path, azure_path, mimetype='image/jpeg'):
    #object_name #str(uuid.uuid4())
    blob = BlobClient.from_connection_string(conn_str=CONNECTION_STRING, container_name=CONTAINER_NAME, blob_name=azure_path)
    #print(blob_client)

    print("\nUploading to Azure Storage as blob:\n\t" + azure_path)

    # Upload the created file
    with open(file=input_path, mode="rb") as data:
        blob.upload_blob(data,overwrite=True)

    #print(blob.__dict__)
        
    return True, "%s/%s" % (returnBasePath(), blob.blob_name)

# upload base64 file
# s3_file_name - file path in s3 bucket - string
# image_base64 - base64 encoded string - string
# mimetype - mimetype of image

def upload_base64file(base64_string, azure_path, mimetype='image/jpeg'):
    blob = BlobClient.from_connection_string(conn_str=CONNECTION_STRING, container_name=CONTAINER_NAME, blob_name=azure_path)

    print("\nUploading to Azure Storage as blob:\n\t" + azure_path)

    # Upload the created file
    base64Obj = base64.decodebytes(base64_string.encode())
    blob.upload_blob(base64Obj,overwrite=True)
    #print(blob.__dict__)
        
    return True, "%s/%s" % (returnBasePath(), blob.blob_name)


# download file from s3 bucket
# file_name - full path of s3 bucket
def download_file(file_name):
    output = 'downloads/'+file_name

    blob = BlobClient.from_connection_string(conn_str=CONNECTION_STRING, container_name=CONTAINER_NAME, blob_name=file_name)

    #print("\nDownloading blob to \n\t" + output)

    with open(file=output, mode="wb") as download_file:
        blob_data = blob.download_blob()
        blob_data.readinto(download_file)

    return output

# list files in s3 bucket
def list_files():
    contents = []
    container = ContainerClient.from_connection_string(conn_str=CONNECTION_STRING, container_name=CONTAINER_NAME)

    blob_list = container.list_blobs()
    for blob in blob_list:
        #print(blob)
        contents.append(blob.name)

    return contents
