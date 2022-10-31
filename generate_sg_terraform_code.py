import boto3.session

my_session = boto3.session.Session(
    profile_name='',
    region_name=''
)

vpc_id = ''

client = my_session.client('ec2')
response = client.describe_security_groups()

fw = open('./terraform-code.sh', 'w')

sg_code_block = {
    'init': 'resource "aws_security_group" ',
    'end': '}',
    'name': 'name = ',
    'description': 'description = ',
    'vpc_id': 'vpc_id',
    'ingress': {
        'init': 'ingress {',
        'from': 'from_port =',
        'to': 'to_port = ',
        'protocol': 'protocol = ',
        'cidr_blocks': 'cidr_blocks = [',
        'security_groups': 'security_groups = [',
        'self': 'self = ',
        'end': '}'
    }
}

f_out = ''

for sg in response['SecurityGroups']:
    if sg['VpcId'] == vpc_id:
        tf_resources_name = sg['VpcId'] + '-' + sg['GroupName']
        sg_id = sg['GroupId']
        tf_command = 'terraform import aws_security_group.' + tf_resources_name + ' ' + sg_id + '\n'
        f_out = f_out + tf_command

fw.write(f_out)
