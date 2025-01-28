from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
import json
import os
import re

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_USER_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn


def clear_results_file():
    # Clear the entire JSON file at the start of the script
    with open('results.json', 'w') as json_file:
        json.dump({}, json_file)


def get_key_words(keys):
    # Convert to lowercase
    key_words = keys.lower()
    # Remove all non-alphanumeric characters except commas and spaces
    key_words = re.sub(r'[^a-z0-9, ]', '', key_words)
    # Replace multiple spaces with a single space
    key_words = re.sub(r'\s+', ' ', key_words)
    
    # Tokenize by commas
    comma_tokens = key_words.split(',')
    
    # Process each comma token
    processed_tokens = []
    for token in comma_tokens:
        # Tokenize by spaces
        space_tokens = token.strip().split(' ')
        # Join space tokens with " & "
        comma_token_key_string = ' & '.join(space_tokens)
        # Surround with "(" and ")"
        processed_tokens.append(f'({comma_token_key_string})')
    
    # Join all processed tokens with " | "
    final_output = ' | '.join(processed_tokens)
    
    return final_output  


@app.route('/enron-data/search', methods=['POST'])
def search():

    print(request.json)

    keys = request.json.get('key_words')
    
    if not keys or not isinstance(keys, str):
        return jsonify({'error': 'key_words is required and must be a string!'}), 400
    
    key_words = get_key_words(keys)

    conn = get_db_connection()

    cur = conn.cursor()

    query = """
    SELECT mid, body
    FROM message 
    WHERE to_tsvector('english', preprocessed_subject_and_body) @@ to_tsquery(%s);
    """

    cur.execute(query, (key_words,))

    results = cur.fetchall()
    
    # Clear the results.json file for our new results.
    clear_results_file()

    # Write the results to the results.json file.
    with open('results.json', 'r+') as json_file:
        data = json.load(json_file)
        data["find_keywords_request_keys"] = keys
        data["find_keywords_keys"] = key_words
        data["find_keywords_results_exact_match"] = results
        json_file.seek(0)
        json.dump(data, json_file, indent=4)

    cur.close()
    conn.close()
    return jsonify('')

if __name__ == '__main__':
    python_env = os.getenv('ENV')

    print(f'Starting the app in {python_env} mode...')

    debug = python_env == 'dev'

    app.run(debug=debug)


