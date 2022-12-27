from PIL import Image
import RekognitionClient as rek
import Personalize as pl
import time

class Load_Balancer():
    def __init__(self):
        self.rekognition = rek.Rekognition()
        self.personalize = pl.Personalize(data_loc='data.csv')
        self.max_client_count = 100
        self.max_rtt_time = 0.5
        self.campaign_ARN = 'arn:aws:personalize:eu-central-1:226969685578:campaign/SWE590_Campaign_1'

    def use_aws_services(self, userid, image, client_count):
        start = time.time()
        if client_count < 50:  # bypass rekognition

            rek_return = self.rekognition.use_rekognition(image, 'ALL')
        end = time.time()

        context = {
            'EVENT_TYPE': 'Happy',
            'USER_BEARD': 'No',
            'USER_GENDER': 'Female'
            }

        if (end - start) < self.max_rtt_time:
            return self.personalize.recommend(campaign_arn=self.campaign_ARN, user_id=userid, numResults=2, context=context)

        elif client_count > self.max_client_count:
            return 'None'
