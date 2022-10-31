# Goal format > terraform import aws_security_group.elb_sg sg-903004f8
# list security group id and name (not tag:name).

import boto3.session

my_session = boto3.session.Session(
    profile_name='',
    region_name=''
)

vpc_id = ''

client = my_session.client('ec2')
response = client.describe_security_groups()

fw = open('./terraform-import.sh', 'w')

f_out = "#!/bin/sh\n\n"

for sg in response['SecurityGroups']:
    if sg['VpcId'] == vpc_id:
        tf_resources_name = sg['VpcId'] + '-' + sg['GroupName']
        sg_id = sg['GroupId']
        tf_command = 'terraform import aws_security_group.' + tf_resources_name + ' ' + sg_id + '\n'
        f_out = f_out + tf_command

fw.write(f_out)
