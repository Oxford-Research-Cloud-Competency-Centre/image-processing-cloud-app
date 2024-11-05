import cv2
from flask import Flask, render_template, request, redirect, url_for
import boto3
from werkzeug.utils import secure_filename
from app.image_processor import process_image
from app.database import insert_metadata, get_metadata
from datetime import datetime
import tempfile
import os
from decimal import Decimal
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

REGION_NAME = os.getenv('REGION_NAME')
S3_BUCKET = os.getenv('S3_BUCKET')

# Create S3 client with the specified region
s3 = boto3.client(
    's3', 
    region_name=REGION_NAME,
    config=boto3.session.Config(s3={'addressing_style': 'path'}, signature_version='s3v4')
    )

@app.route('/')
def index():
    metadata = get_metadata()
    return render_template('dashboard.html', metadata=metadata)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)

        # Create a temporary file to hold the uploaded image with the same extension
        ext = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file_path = temp_file.name
            file.save(temp_file_path)
            
        # Get the size of the original image
        original_image_size_bytes = os.path.getsize(temp_file_path)
        original_image_size_kb = round(Decimal(original_image_size_bytes) / Decimal(1024), 2)

        # Upload original image to S3 inside the 'uploads' directory
        s3.upload_file(temp_file_path, S3_BUCKET, f'uploads/{filename}')

        # Process the uploaded file
        processed_image = process_image(temp_file_path)

        # Save processed image to a temporary file with the same extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as processed_temp_file:
            processed_temp_file_path = processed_temp_file.name
            cv2.imwrite(processed_temp_file_path, processed_image)
            
        # Get the size of the processed image
        processed_image_size_bytes = os.path.getsize(processed_temp_file_path)
        processed_image_size_kb = round(Decimal(processed_image_size_bytes) / Decimal(1024), 2)

        # Upload processed image to S3
        processed_filename = 'processed_' + filename
        s3.upload_file(processed_temp_file_path, S3_BUCKET, f'processed/{processed_filename}')
        
        # Additional metadata
        # Generate a unique ID for the upload
        image_id = str(uuid.uuid4())
        upload_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        description = request.form.get('description', '')

        # Insert metadata into DynamoDB
        insert_metadata(image_id, filename, original_image_size_kb, processed_filename, processed_image_size_kb, upload_date, description)

        # Clean up temporary files
        os.remove(temp_file_path)
        os.remove(processed_temp_file_path)

        # Redirect to index route to display updated data
        return redirect(url_for('index'))

    return redirect(url_for('index'))


@app.route('/download/<filename>')
def download_file(filename):
    try:
        # Define the full S3 object key including the directory
        s3_object_key = f'processed/{filename}'
        # Generate a pre-signed URL for the S3 object
        pre_signed_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': s3_object_key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        # Redirect to the pre-signed URL
        return redirect(pre_signed_url)
    except Exception as e:
        print(f"Exception: {e}")
        return str(e), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
