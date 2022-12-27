import boto3
import json
import time


# current location of the data (give it as an input): 's3://swe590bucket/data.csv'
# when calling the recommender context should be in this format
#             {
#                 'EVENT_TYPE': 'Happy',
#                 'USER_BEARD': 'No',
#                 'USER_GENDER': 'Female'
#             }

class Personalize:
    def __init__(self, data_loc, train=False):

        if train:
            self.personalize = boto3.client('personalize')
            # Read schema from json file
            with open('schema.json', 'r') as f:
                self.schema = json.load(f)

            interactions_schema_arn = self.create_schema()  # create Schema using the schema file
            datasetGroup_arn = self.create_dataset()  # create dataset group

            # create interaction between dataset group and the schema
            interaction_arn = self.create_interaction(interactions_schema_arn, datasetGroup_arn)

            self.create_job(interaction_arn, data_loc)  # create job using the train data nad the interaction
            solutionVersion_arn = self.create_solution(datasetGroup_arn)  # create the solution (model)

            # deploy the solution (campaign_arn can be used to call the model for recommendation)
            self.campaign_arn = self.create_campaign(solutionVersion_arn)

    @staticmethod
    def recommend(campaign_arn, user_id, numResults, context=None):
        personalizeRt = boto3.client('personalize-runtime')
        response = personalizeRt.get_recommendations(
            campaignArn=campaign_arn,
            userId=user_id,
            numResults=numResults,
            context=context
        )
        #print(response['itemList'].__class__)
        return response['itemList']

    def create_schema(self):
        create_interactions_schema_response = self.personalize.create_schema(
            name='SWE590_Schema_4',
            schema=json.dumps(self.schema)
        )

        interactions_schema_arn = create_interactions_schema_response['schemaArn']
        return interactions_schema_arn

    def create_dataset(self):
        response = self.personalize.create_dataset_group(name='SWE590_Dataset')
        dataset_group_arn = response['datasetGroupArn']

        description = self.personalize.describe_dataset_group(datasetGroupArn=dataset_group_arn)['datasetGroup']
        return description['datasetGroupArn']

    def create_interaction(self, schema_ARN, dataset_ARN):
        response = self.personalize.create_dataset(
            name='SWE590_Interaction',
            schemaArn=schema_ARN,
            datasetGroupArn=dataset_ARN,
            datasetType='Interactions'
        )

        dataset_arn = response['datasetArn']
        return dataset_arn

    def create_job(self, dataset_Interaction_ARN, data_loc):
        response = self.personalize.create_dataset_import_job(
            jobName='SWE590_Job',
            datasetArn=dataset_Interaction_ARN,
            dataSource={'dataLocation': data_loc},
            roleArn='arn:aws:iam::226969685578:role/SWE590_Role',
            importMode='FULL'
        )

        dataset_interactions_import_job_arn = response['datasetImportJobArn']

        description = self.personalize.describe_dataset_import_job(
            datasetImportJobArn=dataset_interactions_import_job_arn)['datasetImportJob']

        print('Name: ' + description['jobName'])
        print('ARN: ' + description['datasetImportJobArn'])
        print('Status: ' + description['status'])

        max_time = time.time() + 3 * 60 * 60  # 3 hours
        while time.time() < max_time:
            describe_dataset_import_job_response = self.personalize.describe_dataset_import_job(
                datasetImportJobArn=dataset_interactions_import_job_arn
            )
            status = describe_dataset_import_job_response["datasetImportJob"]['status']
            print("Interactions DatasetImportJob: {}".format(status))

            if status == "ACTIVE" or status == "CREATE FAILED":
                break

            time.sleep(60)

        return description['datasetImportJobArn']

    def create_solution(self, dataset_ARN):
        create_solution_response = self.personalize.create_solution(
            name='SWE590_Solution',
            recipeArn='arn:aws:personalize:::recipe/aws-user-personalization',
            datasetGroupArn=dataset_ARN
        )
        solution_arn = create_solution_response['solutionArn']

        create_solution_version_response = self.personalize.create_solution_version(
            solutionArn=solution_arn
        )

        solution_version_arn = create_solution_version_response['solutionVersionArn']
        print(json.dumps(create_solution_version_response, indent=2))

        max_time = time.time() + 3 * 60 * 60  # 3 hours
        while time.time() < max_time:
            describe_solution_version_response = self.personalize.describe_solution_version(
                solutionVersionArn=solution_version_arn
            )
            status = describe_solution_version_response["solutionVersion"]["status"]
            print("SolutionVersion: {}".format(status))

            if status == "ACTIVE" or status == "CREATE FAILED":
                break

            time.sleep(60)
        return solution_version_arn

    def create_campaign(self, solution_Version_ARN):
        response = self.personalize.create_campaign(
            name='SWE590_Campaign',
            solutionVersionArn=solution_Version_ARN
        )

        arn = response['campaignArn']

        description = self.personalize.describe_campaign(campaignArn=arn)['campaign']
        print('Name: ' + description['name'])
        print('ARN: ' + description['campaignArn'])
        print('Status: ' + description['status'])

        return description['campaignArn']
