import boto3
import os

def lambda_handler(event, context):
    project_tag = os.environ.get('PROJECT_TAG', 'consultor-juridico')
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    for region in regions:
        ec2 = boto3.resource('ec2', region_name=region)
        print("Region:", region)

        # Filtrar instâncias desligadas com a tag Project específica
        instances = ec2.instances.filter(
            Filters=[
                {'Name': 'instance-state-name', 'Values': ['stopped']},
                {'Name': 'tag:Project', 'Values': [project_tag]}
            ])

        for instance in instances:
            instance.start()
            print(f'Started instance: {instance.id} ({instance.tags})')

    return {
        'statusCode': 200,
        'body': f'Start EC2 instances with Project tag: {project_tag} completed'
    }