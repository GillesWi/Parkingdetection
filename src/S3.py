import boto3
from botocore.exceptions import ClientError


def get_image():
    BUCKET_NAME = 'veraxe2'  # replace with your bucket name
    KEY = 'parking.jpg'  # replace with your object key
    s3 = boto3.resource('s3')

    PATH = '../image/'
    # download the file
    try:
        s3.Bucket(BUCKET_NAME).download_file(KEY, PATH)
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
