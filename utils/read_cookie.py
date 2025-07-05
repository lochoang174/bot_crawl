import json
import os

def read_cookie_file(relative_path):
    """
    Reads a JSON file containing cookies and parses it into a dictionary.

    :param relative_path: The relative path to the cookie JSON file.
    :return: A list of dictionaries representing cookies.
    """
    try:
        # Get the absolute path of the file
        base_dir = os.path.dirname(__file__)  # Current script directory
        file_path = os.path.join(base_dir, relative_path)

        # Read and parse the JSON file
        with open(file_path, 'r') as file:
            cookies = json.load(file)

        print("✅ Successfully read and parsed the cookie file.")
        return cookies
    except FileNotFoundError:
        print(f"❌ Cookie file not found at: {relative_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error decoding JSON: {e}")
        return []
