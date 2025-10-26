import json  # Importing the JSON module to handle JSON data
import os    # Importing the OS module to handle file paths

# filename = 'simulation_parameters.json'
# os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure the directory exists

class JSONStorage:

    def __init__(self, filename='parameters.json'):
        self.filename = filename

    def save_to_json(self, params):
        try:
            if not self.filename:
                raise ValueError("Filename must be provided")
            
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)  # Ensure the directory exists

            with open(self.filename, 'w') as f:
                json.dump(params, f, indent=4)  # Write the parameters to a JSON file with indentation

            print(f"Parameters successfully saved to {self.filename}")
            return True
        
        except Exception as e:
            print(f" Error saving parameters: {str(e)}")
            return False

    def load_from_json(self):
        try:
            if not self.filename:
                raise ValueError("Filename must be provided")
            
            with open(self.filename, 'r') as f:
                params = json.load(f)  # Load the parameters from the JSON file

            print(f"Parameters successfully loaded from {self.filename}")
            return params
        
        except Exception as e:
            print(f" Error loading parameters: {str(e)}")
            return False

def save_to_json(params, filename='parameters.json'):
    try:
        if not filename:
            raise ValueError("Filename must be provided")
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure the directory exists

        with open(filename, 'w') as f:
            json.dump(params, f, indent=4)  # Write the parameters to a JSON file with indentation

        print(f"Parameters successfully saved to {filename}")
        return True
    
    except Exception as e:
        print(f" Error saving parameters: {str(e)}")
        return False


# Example with hierarchical structure
parameters = {
    'server': {
        'port': 8000,
        'host': 'localhost',
        'ssl': {
            'enabled': True,
            'certificate_path': '/path/to/cert',
            'key_path': '/path/to/key'
        }
    },
    'database': {
        'connections': {
            'primary': {
                'host': 'db1.example.com',
                'port': 5432,
                'username': 'admin',
                'password': 'secret'
            },
            'backup': {
                'host': 'db2.example.com',
                'port': 5432,
                'username': 'admin',
                'password': 'secret'
            }
        }
    }
}

success = save_to_json(parameters, 'adapters/simulation_parameters.json')