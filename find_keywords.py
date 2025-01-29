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

SIMILARITY_THRESHOLD = 0.6

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_USER_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )
    return conn


def prepare_results_file(request_keys, and_or_key_word_string, key_words_list):
    # Open the file (using 'w' mode because this clears the files contents by truncating it to zero length)
    # and write the metadata to the file.
    with open(RESULTS_FILE, 'w') as json_file:
        metadata = {
            "find_keywords_request_keys": request_keys,
            "find_keywords_and_or_key_word_string": and_or_key_word_string,
            "find_keywords_misspelling_allowed_key_words": key_words_list,
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
    
    return final_output, key_words.split()


def execute_exact_match_queries(cur, and_or_key_word_string):
    match_type = 'exact_match' 

    query_string = """
    -- SELECT DISTINCT mid, body
    SELECT DISTINCT mid, sender
    FROM message 
    WHERE to_tsvector('english', preprocessed_subject_and_body) @@ to_tsquery(%s);
    """
    
    cur.execute(query_string, (and_or_key_word_string,))

    # Fetch and process results in chunks.
    current_chunk = 1
    current_records = 1
    while True:
        chunk = cur.fetchmany(CHUNK_SIZE)
        if not chunk:  # Break when no more rows are fetched from the database.
            break
            
        print(f'{FILE_NAME} is processing "{match_type}" (chunk size {CHUNK_SIZE}) | query string -> {and_or_key_word_string} | current chunk -> {current_chunk} | processing records -> {current_records} to {current_records + len(chunk)}')
        current_records += len(chunk)

        # Append each row as a standalone JSON object.
        with open(RESULTS_FILE, 'a') as json_file:
            for row in chunk:
                json_file.write(json.dumps({
                    "match_type": match_type,
                    "mid": row[0],
                    "body": row[1],
                }) + '\n')
        
        current_chunk += 1


def execute_misspelling_allowed_match_queries(cur, key_words_list):
    match_type = 'misspelling_allowed_match' 

    for word in key_words_list:
        query_string = """
        --SELECT DISTINCT m.mid, m.body
        SELECT DISTINCT m.mid, m.sender
        FROM 
            message m
        INNER JOIN 
            preprocessed_text_single_words p ON m.mid = p.mid
        WHERE 
            similarity(p.word, %s) > %s
        """
        cur.execute(query_string, (word, SIMILARITY_THRESHOLD,))
        
        # Fetch and process results in chunks.
        current_chunk = 1
        current_records = 1
        while True:
            chunk = cur.fetchmany(CHUNK_SIZE)
            if not chunk:  # Break when no more rows to fetch.
                break
                
            print(f'{FILE_NAME} is processing "{match_type}" (chunk size {CHUNK_SIZE}) for word "{word}" | query string -> {key_words_list} | current chunk -> {current_chunk} | processing records -> {current_records} to {current_records + len(chunk)}')
            current_records += len(chunk)

            # Append each row as a standalone JSON object.
            with open(RESULTS_FILE, 'a') as json_file:
                for row in chunk:
                    json_file.write(json.dumps({
                        "match_type": match_type,
                        "mid": row[0],
                        "body": row[1],
                    }) + '\n')
            
            current_chunk += 1


@app.route('/enron-data/search', methods=['POST'])
def search():
    print(request.json)

    request_keys = request.json.get('key_words')
    if not request_keys or not isinstance(request_keys, str):
        return jsonify({'error': 'key_words is required and must be a string!'}), 400
    
    and_or_key_word_string, key_words_list = get_key_words(request_keys)

    print(f'and_or_key_word_string: {and_or_key_word_string} || key_words_list: {key_words_list}')

    conn = get_db_connection()
    cur = conn.cursor()

    prepare_results_file(request_keys, and_or_key_word_string, key_words_list)

    execute_exact_match_queries(cur, and_or_key_word_string)
    execute_misspelling_allowed_match_queries(cur, key_words_list)

    cur.close()
    conn.close()

    return jsonify({'message': f'Search completed and results have been saved in the {RESULTS_FILE} file.'})


if __name__ == '__main__':
    python_env = os.getenv('ENV')

    print(f'Starting the app in "{python_env}" mode...')

    debug = (python_env == 'dev')

    app.run(debug=debug)


