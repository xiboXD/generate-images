from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from utils import *
from openai import OpenAI
from random import shuffle
from datetime import datetime

app = Flask(__name__)
CORS(app)

OUTPUT_FOLDER = 'output_json'
OUTPUT_HTML_FOLDER = 'output_html'

def load_sample_items(file_path):
    with open(file_path, 'r') as file:
        sample_items = json.load(file)
    return sample_items

def create_output_folder():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_folder_path = os.path.join(OUTPUT_FOLDER, timestamp)
    os.makedirs(output_folder_path, exist_ok=True)
    return output_folder_path

def save_html_to_file(html_content, timestamp):
    html_filename = os.path.join(OUTPUT_HTML_FOLDER, f'generated_html_{timestamp}.html')
    with open(html_filename, 'w') as f:
        f.write(html_content)

def generate_html(sample_items, base_prompt):
    output_folder_path = create_output_folder()
    count = 0
    table_rows = []

    for sample_item in sample_items:
        name = sample_item['name']
        output_filename = os.path.join(output_folder_path, f'{name.replace("/", "-")}.json')

        if os.path.isfile(output_filename):
            continue

        with open(output_filename, 'w') as outfile:
            pass

        prompt = 'DMP Prompt: ' + base_prompt + ' Keep all the characteristics:\n'+sample_item['desc'] + ', seed: 1031970432'
        doc = create_variation_dalle(name, prompt, True)
        doc['name'] = name
        print(doc['dalle']['data'][0]['url'])
        with open(output_filename, 'w') as outfile:
            json.dump(doc, outfile)

        image_data_base64 = doc.get('image', '')  
        image_src = f"data:image/png;base64,{image_data_base64}"
        revised_prompt = doc.get('dalle', {}).get('data', [{}])[0].get('revised_prompt', '')
        row = f"<tr><td>{name}</td><td><img src='{image_src}' width='200px'></td><td>{revised_prompt}</td></tr>"
        table_rows.append(row)

        count += 1
        if count >= 4:
            break

    header = "<tr><th>Name</th><th>Image</th><th>Revised Prompt</th></tr>"
    table_content = ''.join(table_rows)
    table = f"<table>{header}{table_content}</table>"

    save_html_to_file(table, output_folder_path.split('/')[-1])

    return table

@app.route('/generate_image', methods=['POST'])
def generate_html_api():
    data = request.get_json()
    base_prompt = data.get('prompt', '')

    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
    client = OpenAI()

    sample_items = load_sample_items("sample_items.json")
    shuffle(sample_items)

    html_table = generate_html(sample_items, base_prompt)

    return html_table

@app.route('/image_data', methods=['GET'])
def get_image_data():
    with open('image_data.json', 'r') as file:
        image_data = json.load(file)
    return jsonify(image_data)

if __name__ == "__main__":
    app.run(debug=True)
