import json

if __name__ == '__main__':
    f = open('./terraforming.json', 'r')
    fw = open('./new_state.json', 'w')
    origin_state = json.load(f)
    resources = origin_state['modules'][0]['resources']
    output_state = '[\n'
    for key in resources:
        new_obj = {
            'type': resources[key]['type'],
            'mode': 'managed',
            'provider': "provider[\"registry.terraform.io/hashicorp/aws\"]",
            'instances': [].append({
                "schema_version": 1,
                "sensitive_attributes": [],
                "private": "",
                "dependencies": [
                    "aws_vpc.this"
                ],
                "attributes": resources[key]['primary']['attributes']
            })
        }

        output_state = output_state + json.dumps(resources[key]) + ",\n"

    output_state = output_state + ']'
    output_state = fw.write(output_state)