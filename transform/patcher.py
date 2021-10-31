import boto3
from urllib.parse import unquote_plus


def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    ssm_client = boto3.client('ssm')
    
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = unquote_plus(record['s3']['object']['key'])
        override_doc = "s3://" + bucket + "/" + key
        instance_id = key.split("/")[-1].replace(".yaml","")
        print("Overide Doc {} on instance {} ".format(override_doc,instance_id) )

        response = ssm_client.send_command( DocumentName="AWS-RunPatchBaseline",
            InstanceIds=[instance_id],
            Parameters= {
                'Operation': ['Install'],'SnapshotId':[''],'RebootOption':['RebootIfNeeded'],'InstallOverrideList':[override_doc],'BaselineOverride':['']
            },
            TimeoutSeconds=600)
        print(response)
#aws ssm send-command --document-name "AWS-RunPatchBaseline" 
#--document-version "1" --targets '[{"Key":"InstanceIds","Values":["i-062a3de7156ffc441"]}]' 
#--parameters '{"Operation":["Install"],"SnapshotId":[""],"InstallOverrideList":["s3://sm-patch-output/i-062a3de7156ffc441.yaml"],"BaselineOverride":[""],"RebootOption":["RebootIfNeeded"]}'
#--timeout-seconds 600 --max-concurrency "50" --max-errors "0" --region us-east-1        
