import os
from base64 import b64encode
import json

def load_images_as_base64(data_folder):
    images_dict = {}
    for filename in os.listdir(data_folder):
        if filename.endswith('.png'):
            with open(os.path.join(data_folder, filename), 'rb') as image_file:
                images_dict[b64encode(image_file.read()).decode('utf-8')] = filename.replace('.png', '')
    return images_dict

# Example usage
images_base64_dict = load_images_as_base64('data')
print(json.dumps(images_base64_dict, indent=4))
