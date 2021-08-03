import json
import boto3
import mimetypes
import zipfile
from io import BytesIO

def lambda_handler(event, context):
    # TODO implement
    # Get s3 bucket and object info　from event
    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    s3_obj = event['Records'][0]['s3']['object']['key']
    s3_obj_size = event['Records'][0]['s3']['object']['size']
    
    s3_resource = boto3.resource('s3')
    
    try:
        epub_obj = s3_resource.Object(
            bucket_name=s3_bucket,
            key=s3_obj
        )
    except Exception as e:
        print(e)
    
    buffer = BytesIO(epub_obj.get()['Body'].read())
    z = zipfile.ZipFile(buffer)
    
    # Read each file
    for filename in z.namelist():
        file_info = z.getinfo(filename)
        
        # Guess ContentType of file
        filetype = mimetypes.MimeTypes().guess_type(file_info.filename)[0]
        
        if filetype == None:
            filetype = 'binary/octet-stream'
        
        # Upload to corresponding folder in S3 bucket
        try:
            s3_resource.meta.client.upload_fileobj(
                z.open(filename),
                Bucket=s3_bucket,
                Key=f'{s3_obj}/{filename}',
                ExtraArgs={
                    'ContentType': filetype
                }
            )
        except Exception as e:
            print(e)
    
    return 0
