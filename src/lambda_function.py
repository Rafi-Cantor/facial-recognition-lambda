import json
import boto3
from urllib.parse import unquote_plus

BUCKET = "facial-recognition-app-upload-bucket"
DYNAMO_DB_TABLE = "faceprints"

s3 = boto3.client("s3", region_name='eu-west-2')
rekognition = boto3.client('rekognition', region_name='eu-west-2')
dynamodb = boto3.client('dynamodb', region_name='eu-west-2')


def lambda_handler(event, context):
    print(event)
    image_key = event["Records"][0]["s3"]["object"]["key"]
    unquote_key = unquote_plus(image_key)
    print(unquote_plus(image_key))

    response = rekognition.index_faces(
        Image={
            "S3Object":
                {
                    "Bucket": BUCKET,
                    "Name": unquote_key
                }
        },
        MaxFaces=1,
        CollectionId="facial-recognition-app"
    )
    print(response)
    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code != 200:
        raise ValueError(f"Something went wrong whilst creating a face print for {image_key}"
                         f". returned {status_code} code")

    face_id = response['FaceRecords'][0]['Face']['FaceId']
    metadata = s3.get_object(Bucket=BUCKET, Key=unquote_key)
    full_name = metadata["Metadata"]["full_name"]
    dynamodb.put_item(
        TableName=DYNAMO_DB_TABLE,
        Item={
            "face_id": {'S': face_id},
            "full_name": {'S': full_name}
        }
    )

