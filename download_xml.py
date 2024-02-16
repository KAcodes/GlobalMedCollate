"""Script downloads relevant disease XML from pharmazer input on S3 bucket"""
from os import path, mkdir, environ

from dotenv import load_dotenv
from boto3 import client

S3_DOWNLOAD_FOLDER = "downloaded_xmls"

def get_object_keys(s3_client: client, bucket: str) -> list[str]:
    """Returns a list of object keys from a given bucket."""

    contents = s3_client.list_objects(Bucket=bucket)["Contents"]
    keys = sorted(contents, key=lambda x: x["LastModified"])
    return [obj["Key"] for obj in keys]


def get_relevant_files(files: list) -> list:
    """Gets only csv files from relevant downloaded files"""

    return [key for key in files if key.startswith("c9-kayode-input") and key.endswith("xml")]


def download_most_recent_xml(s3_client: client, bucket: str) -> str:
    """Downloads most recent xml file from c9-kayode-input bucket."""

    xml_object_keys = get_object_keys(s3_client, bucket)

    most_recent_key = get_relevant_files(xml_object_keys)[-1]

    if not path.exists(f"{S3_DOWNLOAD_FOLDER}"):
        mkdir(f"{S3_DOWNLOAD_FOLDER}")

    base_filename = path.basename(most_recent_key)
    s3_client.download_file(bucket, most_recent_key, f"{S3_DOWNLOAD_FOLDER}/{base_filename}")

    return base_filename


if __name__ == "__main__":

    load_dotenv()
    s3 = client("s3",
    aws_access_key_id=environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=environ["AWS_SECRET_ACCESS_KEY"])

    download_most_recent_xml(s3, "sigma-pharmazer-input")
    