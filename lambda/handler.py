"""

"""

import os
import hashlib
import ffmpeg
import boto3
from botocore.exceptions import ClientError
import requests

def get_secret():

    secret_name = "PE_DB_S3_CLIENT"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    
    return secret

secret = get_secret()

s3_client = boto3.client('s3',
                         aws_access_key_id=secret.get('access_key_id'),
                         aws_secret_access_key=secret.get('secret_access_key'))
DATABASE_NAME = 'pose-estimation-db'

def download_video_from_url(url: str):
    """
    Downloads a video from a given URL and returns the path to the downloaded file.
    """
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to download video from {url}")

        filename = os.path.basename(url)
        
        tmp = f'/tmp/{filename}'
        with open(tmp, 'wb') as f:
            f.write(response.content)
            
        return tmp
    
    except Exception as e:
        raise Exception(f"Failed to download video from {url}: {e}")
    
def check_s3_folder_exists(key: str) -> bool:
    """Checks if a folder exists in an S3 bucket."""
    response = s3_client.list_objects_v2(Bucket=DATABASE_NAME, Prefix=key)

    for obj in response.get('Contents', []):
        if obj['Key'].startswith(key):
            return True

    return False

def generate_project_name(url: str) -> str:
    """Generates a unique project name using a URL."""
    return hashlib.md5(url.encode()).hexdigest()

def check_if_user_exists(input: dict) -> bool:
    """Returns True if user exists in `pose-estimation-db` S3 bucket."""
    user_folder = f"{input['userID']}/"
    return check_s3_folder_exists(user_folder)

def create_user_folder(input: dict) -> str:
    """Creates a new user folder in `pose-estimation-db` S3 bucket if user doesn't exist."""
    
    user_folder = f"{input['userID']}/"
    msg = ''
    if not check_if_user_exists(input):
        response = s3_client.put_object(Bucket=DATABASE_NAME, 
                             Key=user_folder)
        
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            msg = f"User folder '{user_folder}' created successfully"
            print(msg)
        else:
            msg = f"Failed to create user folder '{user_folder}'"
            print(msg)
    else:
        msg = f"User folder '{user_folder}' already exists"
        print(msg)
    return msg

def check_if_user_project_exists(input: dict) -> bool:
    """Returns True if `user` and `project` exists in `pose-estimation-db` S3 bucket."""
    project_folder = f"{input['userID']}/{input['fileID']}"
    return check_s3_folder_exists(project_folder)

def generate_project_key(input: dict) -> str:
    """Generates the project key for a user/project in `pose-estimation-db` S3 bucket."""
    project_name = generate_project_name(input['inputURL'])
    return f"{input['userID']}/{project_name}/frames"

def create_project_folder(input: dict) -> str:
    """Creates a project folder for a user/project in `pose-estimation-db` S3 bucket."""
    msg = ''
    if not check_if_user_project_exists(input):
        project_key = generate_project_key(input)
        response = s3_client.put_object(Bucket=DATABASE_NAME, Key=project_key)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            msg = f"Project folder '{project_key}' created successfully"
            print(msg)
        else:
            msg = f"Failed to create project folder '{project_key}'"
            print(msg)
    else:
        msg = f"Project folder '{project_key}' already exists"
        print(msg)
    return msg

def extract_frames_from_video(video_path, output_directory, frame_rate=1):
    output_pattern = os.path.join(output_directory, 'frame-%03d.jpg')
    try:
        ffmpeg.input(video_path).output(output_pattern, r=frame_rate).run()
        print(f"Frames extracted successfully and saved in {output_directory}.")
    except ffmpeg.Error as e:
        print(f"Error occurred: {e.stderr}")

def upload_frames_to_s3(frames_directory, bucket_name):
    s3_client = boto3.client('s3')
    for root, dirs, files in os.walk(frames_directory):
        for file in files:
            file_path = os.path.join(root, file)
            s3_key = os.path.join('frames', file)  # You can customize the S3 key as per your requirement.
            s3_client.upload_file(file_path, bucket_name, s3_key)

def lambda_handler(event, context):
    try:
        video_path = download_video_from_url(event['url'])
        frames_output_directory = '/tmp/frames'
        os.makedirs(frames_output_directory, exist_ok=True)
        
        extract_frames_from_video(video_path, frames_output_directory, frame_rate=1)
        
        s3_bucket_name = "YOUR_S3_BUCKET_NAME"  # Replace with your S3 bucket name
        upload_frames_to_s3(frames_output_directory, s3_bucket_name)

        return {
            "statusCode": 200,
            "body": "Video frames extracted and uploaded successfully to S3",
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }