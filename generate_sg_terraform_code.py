import json
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
    'tags': 'tags = {',
    'ingress': {
        'init': 'ingress {',
        'from': 'from_port = ',
        'to': 'to_port = ',
        'protocol': 'protocol = ',
        'cidr_blocks': 'cidr_blocks = ',
        'security_groups': 'security_groups = '
    },
    'egress': {
        'init': 'egress {',
        'from': 'from_port = ',
        'to': 'to_port = ',
        'protocol': 'protocol = ',
        'cidr_blocks': 'cidr_blocks = ',
        'security_groups': 'security_groups = '
    }
}

f_out = ''

for sg in response['SecurityGroups']:
    if sg['VpcId'] == vpc_id:
        tf_code = sg_code_block['init'] + "\"" + sg['VpcId'] + "-" + sg['GroupName'] + "\" {\n" + \
                  "\t" + sg_code_block['name'] + "\"" + sg['GroupName'] + "\"\n" + \
                  "\t" + sg_code_block['description'] + "\"" + sg['Description'] + "\"\n" + \
                  "\t" + sg_code_block['vpc_id'] + "\"" + sg['VpcId'] + "\"\n"
        # Ingress
        for ingress in sg['IpPermissions']:
            # Source : CIDR
            if len(ingress['IpRanges']) > 0:
                map_description = {}
                for cidr in ingress['IpRanges']:
                    if 'Description' in cidr:
                        if cidr['Description'] in map_description:
                            map_description[cidr['Description']].append(cidr['CidrIp'])
                        else:
                            map_description[cidr['Description']] = [cidr['CidrIp']]
                    else:
                        if '' in map_description:
                            map_description[''].append(cidr['CidrIp'])
                        else:
                            map_description[''] = [cidr['CidrIp']]
                for key in map_description:
                    tf_code = tf_code + \
                              "\n\t" + sg_code_block['ingress']['init'] + "\n" + \
                              "\t\t" + sg_code_block['ingress']['protocol'] + "\"" + ingress['IpProtocol'] + "\"\n"
                    if ingress['IpProtocol'] != '-1':
                        tf_code = tf_code + \
                                  "\t\t" + sg_code_block['ingress']['from'] + str(ingress['FromPort']) + "\n" + \
                                  "\t\t" + sg_code_block['ingress']['to'] + str(ingress['ToPort']) + "\n"
                    else:
                        tf_code = tf_code + \
                                  "\t\t" + sg_code_block['ingress']['from'] + " 0 \n" + \
                                  "\t\t" + sg_code_block['ingress']['to'] + " 0 \n"

                    tf_code = tf_code + \
                              "\t\t" + sg_code_block['ingress']['cidr_blocks'] + json.dumps(map_description[key]) + "\n" + \
                              "\t\t" + sg_code_block['description'] + "\"" + key + "\"\n" + \
                              "\t" + sg_code_block['end'] + "\n"

            # Source : Security Group
            if len(ingress['UserIdGroupPairs']) > 0:
                map_description_sg = {}
                for sg_id in ingress['UserIdGroupPairs']:
                    if 'Description' in sg_id:
                        if sg_id['Description'] in map_description_sg:
                            map_description_sg[sg_id['Description']].append(sg_id['GroupId'])
                        else:
                            map_description_sg[sg_id['Description']] = [sg_id['GroupId']]
                    else:
                        if '' in map_description_sg:
                            map_description_sg[''].append(sg_id['GroupId'])
                        else:
                            map_description_sg[''] = [sg_id['GroupId']]
                for key in map_description_sg:
                    tf_code = tf_code + \
                              "\n\t" + sg_code_block['ingress']['init'] + "\n" + \
                              "\t\t" + sg_code_block['ingress']['protocol'] + "\"" + ingress['IpProtocol'] + "\"\n"
                    if ingress['IpProtocol'] != '-1':
                        tf_code = tf_code + \
                                  "\t\t" + sg_code_block['ingress']['from'] + str(ingress['FromPort']) + "\n" + \
                                  "\t\t" + sg_code_block['ingress']['to'] + str(ingress['ToPort']) + "\n"
                    else:
                        tf_code = tf_code + \
                                  "\t\t" + sg_code_block['ingress']['from'] + " 0 \n" + \
                                  "\t\t" + sg_code_block['ingress']['to'] + " 0 \n"

                    if sg['GroupId'] in map_description_sg[key]:
                        map_description_sg[key].remove(sg['GroupId'])
                        if len(map_description_sg[key]) > 0:
                            tf_code = tf_code + \
                                      "\t\t" + sg_code_block['ingress']['security_groups'] + json.dumps(map_description_sg[key]) + "\n" + \
                                      "\t\t" + sg_code_block['description'] + "\"" + key + "\"\n" + \
                                      "\t\t" + 'self = true\n'
                        else:
                            tf_code = tf_code + \
                                      "\t\t" + sg_code_block['description'] + "\"" + key + "\"\n" + \
                                      "\t\t" + 'self = true\n'
                    else:
                        tf_code = tf_code + \
                                  "\t\t" + sg_code_block['ingress']['security_groups'] + json.dumps(map_description_sg[key]) + "\n" + \
                                  "\t\t" + sg_code_block['description'] + "\"" + key + "\"\n"

                    tf_code = tf_code + "\t" + sg_code_block['end'] + "\n"

        # Egress
        for egress in sg['IpPermissionsEgress']:
            # Source : CIDR
            if len(egress['IpRanges']) > 0:
                map_description_e = {}
                for cidr in egress['IpRanges']:
                    if 'Description' in cidr:
                        if cidr['Description'] in map_description_e:
                            map_description_e[cidr['Description']].append(cidr['CidrIp'])
                        else:
                            map_description_e[cidr['Description']] = [cidr['CidrIp']]
                    else:
                        if '' in map_description_e:
                            map_description_e[''].append(cidr['CidrIp'])
                        else:
                            map_description_e[''] = [cidr['CidrIp']]
                for key in map_description_e:
                    tf_code = tf_code + \
                              "\n\t" + sg_code_block['egress']['init'] + "\n" + \
                              "\t\t" + sg_code_block['egress']['protocol'] + "\"" + egress['IpProtocol'] + "\"\n"
                    if egress['IpProtocol'] != '-1':
                        tf_code = tf_code + \
                                  "\t\t" + sg_code_block['egress']['from'] + str(egress['FromPort']) + "\n" + \
                                  "\t\t" + sg_code_block['egress']['to'] + str(egress['ToPort']) + "\n"
                    else:
                        tf_code = tf_code + \
                                  "\t\t" + sg_code_block['egress']['from'] + " 0 \n" + \
                                  "\t\t" + sg_code_block['egress']['to'] + " 0 \n"

                    tf_code = tf_code + \
                              "\t\t" + sg_code_block['egress']['cidr_blocks'] + json.dumps(map_description_e[key]) + "\n" + \
                              "\t\t" + sg_code_block['description'] + "\"" + key + "\"\n" + \
                              "\t" + sg_code_block['end'] + "\n"

            # Source : Security Group
            if len(egress['UserIdGroupPairs']) > 0:
                map_description_e_sg = {}
                for sg_id in egress['UserIdGroupPairs']:
                    if 'Description' in sg_id:
                        if sg_id['Description'] in map_description_e_sg:
                            map_description_e_sg[sg_id['Description']].append(sg_id['GroupId'])
                        else:
                            map_description_e_sg[sg_id['Description']] = [sg_id['GroupId']]
                    else:
                        if '' in map_description_e_sg:
                            map_description_e_sg[''].append(sg_id['GroupId'])
                        else:
                            map_description_e_sg[''] = [sg_id['GroupId']]
                for key in map_description_e_sg:
                    tf_code = tf_code + \
                              "\n\t" + sg_code_block['egress']['init'] + "\n" + \
                              "\t\t" + sg_code_block['egress']['protocol'] + "\"" + egress['IpProtocol'] + "\"\n"
                    if egress['IpProtocol'] != '-1':
                        tf_code = tf_code + \
                                  "\t\t" + sg_code_block['egress']['from'] + str(egress['FromPort']) + "\n" + \
                                  "\t\t" + sg_code_block['egress']['to'] + str(egress['ToPort']) + "\n"
                    else:
                        tf_code = tf_code + \
                                  "\t\t" + sg_code_block['egress']['from'] + " 0 \n" + \
                                  "\t\t" + sg_code_block['egress']['to'] + " 0 \n"

                    if sg['GroupId'] in map_description_e_sg[key]:
                        map_description_e_sg[key].remove(sg['GroupId'])
                        if len(map_description_e_sg[key]) > 0:
                            tf_code = tf_code + \
                                      "\t\t" + sg_code_block['egress']['security_groups'] + json.dumps(map_description_e_sg[key]) + "\n" + \
                                      "\t\t" + sg_code_block['description'] + "\"" + key + "\"\n" + \
                                      "\t\t" + 'self = true\n'
                        else:
                            tf_code = tf_code + \
                                      "\t\t" + sg_code_block['description'] + "\"" + key + "\"\n" + \
                                      "\t\t" + 'self = true\n'
                    else:
                        tf_code = tf_code + \
                                  "\t\t" + sg_code_block['egress']['security_groups'] + json.dumps(map_description_e_sg[key]) + "\n" + \
                                  "\t\t" + sg_code_block['description'] + "\"" + key + "\"\n"

                    tf_code = tf_code + "\t" + sg_code_block['end'] + "\n"

        # Tags
        if 'Tags' in sg and len(sg['Tags']) > 0:
            tf_code = tf_code + "\n\t" + sg_code_block['tags'] + "\n"
            for tag in sg['Tags']:
                tf_code = tf_code + "\t\t" +tag['Key'] + " = \"" + tag['Value'] + "\"\n"
            tf_code = tf_code + "\t" + sg_code_block['end'] + "\n"

        tf_code = tf_code + sg_code_block['end'] + "\n\n"
        f_out = f_out + tf_code

fw.write(f_out)
