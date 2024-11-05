import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

REGION_NAME = os.getenv('REGION_NAME')
IMAGE_METADATA_TABLE = os.getenv('IMAGE_METADATA_TABLE')

# Create DynamoDB client within the specified region
dynamodb = boto3.resource('dynamodb', region_name=REGION_NAME)

table = dynamodb.Table(IMAGE_METADATA_TABLE)

def insert_metadata(image_id, original_filename, original_size, processed_filename, processed_size, upload_date, description):
    table.put_item(
        Item={
            'id': image_id,
            'original_filename': original_filename,
            'original_size': original_size,
            'processed_filename': processed_filename,
            'processed_size': processed_size,
            'upload_date': upload_date,
            'description': description
        }
    )

def get_metadata():
    try:
        response = table.scan()
        items = response['Items']
        # Convert the items to a list of lists for the template
        metadata = [
            [
                item.get('id', ''),
                item.get('original_filename', ''),
                item.get('original_size', ''),
                item.get('processed_filename', ''),
                item.get('processed_size', ''),
                item.get('upload_date', ''),
                item.get('description', '')
            ]
            for item in items
        ]
        return metadata
    except (BotoCoreError, ClientError) as e:
        return []
