import boto3.session

my_session = boto3.session.Session(
    profile_name='lstp',
    region_name='ap-northeast-2'
)

vpc_id = 'vpc-09564e60ab65ef393'
# vpc_id = 'vpc-05be2c65b26b44685'

client = my_session.client('ec2')
response = client.describe_security_groups()

fw = open('./terraform-code.tf', 'w')

sg_code_block = {
    'init': 'resource "aws_security_group" ',
    'end': '}',
    'name': 'name = ',
    'description': 'description = ',
    'vpc_id': 'vpc_id = ',
    'ingress': {
        'init': 'ingress {',
        'from': 'from_port = ',
        'to': 'to_port = ',
        'protocol': 'protocol = ',
        'cidr_blocks': 'cidr_blocks = [',
        'security_groups': 'security_groups = [',
    }
}

f_out = ''

for sg in response['SecurityGroups']:
    if sg['VpcId'] == vpc_id:
        tf_code = sg_code_block['init'] + "\"" + sg['VpcId'] + "-" + sg['GroupName'] + "\" {\n\t" + \
                  sg_code_block['name'] + "\"" + sg['GroupName'] + "\"\n\t" + \
                  sg_code_block['description'] + "\"" + sg['Description'] + "\"\n\t" + \
                  sg_code_block['vpc_id'] + "\"" + sg['VpcId'] + "\"\n"
        # print(sg['GroupName'])
        for ingress in sg['IpPermissions']:
            # print(sg['IpPermissions'])
            if len(ingress['IpRanges']) > 0:
                map_description = {}
                for cidr in ingress['IpRanges']:
                    print(cidr['Description'])
                    if cidr['Description'] in map_description:
                        map_description[cidr['Description']].append(cidr['CidrIp'])
                    else:
                        map_description[cidr['Description']] = [cidr['CidrIp']]
                for key in map_description:
                    tf_code = tf_code + \
                              sg_code_block['ingress']['init'] + "\"\n" + \
                              sg_code_block['ingress']['protocol'] + "\"" + ingress['IpProtocol'] + "\""
                    if ingress['IpProtocol'] != '-1':
                        tf_code = tf_code + \
                                  sg_code_block['ingress']['from'] + str(ingress['FromPort']) + "\n" + \
                                  sg_code_block['ingress']['to'] + str(ingress['ToPort'])

                    tf_code = tf_code + \
                              sg_code_block['ingress']['cidr_blocks'] + str(map_description[key]) + \
                              sg_code_block['description'] + "\"" + key + "\"" + \
                              sg_code_block['end']

            if len(ingress['UserIdGroupPairs']) > 0:
                map_description = {}
                for sg_id in ingress['UserIdGroupPairs']:
                    if sg_id['Description'] in map_description:
                        map_description[sg_id['Description']].append(sg_id['GroupId'])
                    else:
                        map_description[sg_id['Description']] = [sg_id['GroupId']]
                for key in map_description:
                    tf_code = tf_code + \
                              sg_code_block['ingress']['init'] + "\"" + \
                              sg_code_block['ingress']['protocol'] + ingress['IpProtocol']
                    if ingress['IpProtocol'] != '-1':
                        tf_code = tf_code + \
                                  sg_code_block['ingress']['from'] + str(ingress['FromPort']) + "\n" + \
                                  sg_code_block['ingress']['to'] + str(ingress['ToPort'])

                    tf_code = tf_code + \
                              sg_code_block['ingress']['security_groups'] + str(map_description[key]) + \
                              sg_code_block['description'] + "\"" + key + "\"" + \
                              sg_code_block['end']

        tf_code = tf_code + sg_code_block['end'] + "\n\n"
        f_out = f_out + tf_code

fw.write(f_out)
