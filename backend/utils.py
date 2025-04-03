import json

def save_to_json(data, output_file):
    """ Save extracted code data to a JSON file """
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {output_file}")
