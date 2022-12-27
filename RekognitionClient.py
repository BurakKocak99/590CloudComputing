import time
import boto3
import io


class Rekognition():
    def __init__(self):
        self.client = boto3.client('rekognition')

    def use_rekognition(self,image,attributes):
        response = self.client.detect_faces(Image={'Bytes': image}, Attributes=[attributes])
        return  response

