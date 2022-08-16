import boto3
from flask_restful import Resource, request
from API.middleware.middleware import validate_request
from config import S3_KEY, S3_SECRET, S3_BUCKET, S3_REGION
from time import time_ns

s3 = boto3.client(
    's3',
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET,
    region_name=S3_REGION
)


class Upload(Resource):
    @validate_request(admin_only=True)
    def post(self):
        file = request.files['file']
        file_name = f'{time_ns()}.jpg'
        s3.upload_fileobj(file, S3_BUCKET, file_name, ExtraArgs={'ACL': 'public-read'})

        file_url = '%s/%s/%s' % (s3.meta.endpoint_url, S3_BUCKET, file_name)
        return {'data': file_url}, 200