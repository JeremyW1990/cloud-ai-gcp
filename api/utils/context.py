import json
import yaml


def json_to_final_yaml_context(json_data):
    # Prepare the data for the new YAML format
    final_data = {
        "context": {
            "name": json_data["context"]["name"],
            "instructions": json_data["context"]["instructions"],
        },
        "agents": [
            {
                "name": agent["name"],
                "instructions": agent["instructions"]
            } for agent in json_data["agents"]
        ]
    }
    
    # Convert the data to YAML content
    yaml_content = yaml.dump(final_data, default_flow_style=False, sort_keys=False)
    
    return yaml_content

