import base64
import math
import os
import time
import boto3
from botocore.exceptions import NoCredentialsError


from tqdm import tqdm
import concurrent.futures

from dotenv import load_dotenv
load_dotenv()

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
REGION_HOST = os.getenv('REGION_HOST')

S3_BASE_URL = os.getenv('S3_BASE_URL')

# initialze boto object
s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)
s3_resource = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY,
                      aws_secret_access_key=AWS_SECRET_KEY)

# upload file from given path
# file_path - file path - string
# object_name - file_path in s3 bucket - string
def upload_file_input(file_path, object_name, mime_type="image/jpeg"):
    s3_client.upload_file(file_path, S3_BUCKET_NAME, object_name, ExtraArgs={'ACL': 'public-read', 'ContentType': mime_type})
    return True, "%s/%s" % (S3_BASE_URL, object_name)

# upload base64 file
# s3_file_name - file path in s3 bucket - string
# image_base64 - base64 encoded string - string
# mimetype - mimetype of image
def upload_base64file(s3_file_name, image_base64, mimetype):
    obj = s3_resource.Bucket(S3_BUCKET_NAME).\
            put_object(Key=s3_file_name,
            Body=base64.b64decode(image_base64),
            ContentType=mimetype,
            ACL='public-read')
    
    return True, "%s/%s" % (S3_BASE_URL, s3_file_name)

# download file from s3 bucket
# file_name - full path of s3 bucket
def download_file(file_name):
    output = 'downloads/'+file_name
    s3_resource.Bucket(S3_BUCKET_NAME).download_file(file_name, output)
    return output

# download files from s3 bucket
# file_name - full path of s3 bucket

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def get_cunks(size_bytes, desired_sections):
    return size_bytes / desired_sections

def s3_get_meta_data(conn, bucket, key):
    meta_data = conn.head_object(
        Bucket=bucket,
        Key=key
    )
    return meta_data

def download_object_in_chunks(object_key, local_directory, parallel_threads=5):

    start = time.time()
    md = s3_get_meta_data(s3_client, S3_BUCKET_NAME, object_key)
    chunk = get_cunks(md["ContentLength"], parallel_threads)
    print("Making %s parallel s3 calls with a chunk size of %s each..." % (
        parallel_threads, convert_size(chunk))
    )
    
    download_path = os.path.join(local_directory, os.path.sep.join(object_key.split("/")[:-1]))
    os.makedirs(download_path, exist_ok=True)
    file_path = os.path.join(download_path, object_key.split("/")[-1])
    print("Downloading %s to %s..." % (object_key, file_path))
    s3_client.download_file(
        Bucket=S3_BUCKET_NAME,
        Filename=file_path,
        Key=object_key,
        Config=boto3.s3.transfer.TransferConfig(
            max_concurrency=parallel_threads
        )
    )
    end = time.time() - start
    print("Finished downloading %s in %s seconds" % (object_key, end))


def download_container_contents(local_directory):

    print("\nKindly wait! Downloading container contents to " + local_directory + "...")

    os.makedirs(local_directory, exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url  = {executor.submit(download_object_in_chunks, item['Key'], local_directory,): item for item in s3_client.list_objects(Bucket=S3_BUCKET_NAME)['Contents']}
        for future in concurrent.futures.as_completed(future_to_url):
            print(future.result())

    print("\nDone!")
    return True

# list files in s3 bucket
def list_files():
    contents = []
    for item in s3_client.list_objects(Bucket=S3_BUCKET_NAME)['Contents']:
        contents.append(item)
    return contents


'''
# s3 bucket policy setting
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "PUT"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": []
    }
]
'''