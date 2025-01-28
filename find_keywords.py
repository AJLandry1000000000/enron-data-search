from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
import json
import os
import re

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

CHUNK_SIZE = 1000

RESULTS_FILE = 'results.ndjson'

FILE_NAME = os.path.basename(__file__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_USER_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn


def prepare_results_file(request_keys, key_words):
    # Open the file (using 'w' mode because this clears the files contents by truncating it to zero length)
    # and write the metadata to the file.
    with open(RESULTS_FILE, 'w') as json_file:
        metadata = {
            "find_keywords_request_keys": request_keys,
            "find_keywords_keys": key_words,
        }
        json_file.write(json.dumps(metadata) + '\n')


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

    request_keys = request.json.get('key_words')
    
    if not request_keys or not isinstance(request_keys, str):
        return jsonify({'error': 'key_words is required and must be a string!'}), 400
    
    key_words = get_key_words(request_keys)
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
    -- SELECT mid, body
    SELECT mid, sender
    FROM message 
    WHERE to_tsvector('english', preprocessed_subject_and_body) @@ to_tsquery(%s);
    """

    cur.execute(query, (key_words,))

    prepare_results_file(request_keys, key_words)

    # Fetch and process results in chunks.
    current_chunk = 1
    current_records = 1
    while True:
        chunk = cur.fetchmany(CHUNK_SIZE)
        if not chunk:  # Break when no more rows to fetch.
            break
            
        print(f'{FILE_NAME} is processing data chunks of size -> {CHUNK_SIZE} | query string -> {key_words} | current chunk -> {current_chunk} | processing records -> {current_records} to {current_records + len(chunk)}')
        current_records += len(chunk)

        # Append each row as a standalone JSON object.
        with open(RESULTS_FILE, 'a') as json_file:
            for row in chunk:
                json_file.write(json.dumps({
                    "mid": row[0],
                    "body": row[1],
                }) + '\n')
        
        current_chunk += 1

    cur.close()
    conn.close()
    return jsonify({'message': f'Search completed and results have been saved in the {RESULTS_FILE} file.'})

if __name__ == '__main__':
    python_env = os.getenv('ENV')

    print(f'Starting the app in "{python_env}" mode...')

    debug = (python_env == 'dev')

    app.run(debug=debug)


