"""Script sends generated csv to pharmazer S3 output bucket"""
from os import environ, path, listdir, remove
from datetime import datetime
import logging

from dotenv import load_dotenv
from boto3 import client
from botocore.exceptions import ClientError


def upload_file(s3_client: client, file: str, bucket: str, object_name=None):
    """Upload a file to an S3 bucket"""

    if object_name is None:
        object_name = path.basename(file)

    try:
        s3_client.upload_file(file, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


if __name__ == "__main__":

    load_dotenv()
    s3 = client("s3",
    aws_access_key_id=environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])

    CURRENT_DATETIME = datetime.now().replace(microsecond=0)
    file_path = listdir("downloaded_xmls")[0]
    file_name = file_path.replace('.xml', '')
    upload_file(
        s3, f"{file_name}.csv", "sigma-pharmazer-output",
        f"c9-kayode-output/{file_name}-{CURRENT_DATETIME}.csv"
    )

    remove(f"downloaded_xmls/{file_name}.xml")
    remove(f"{file_name}.csv")
