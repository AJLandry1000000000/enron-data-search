from flask import Flask, request, jsonify
import psycopg2
from dotenv import load_dotenv
import json
import os
import re

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Import functions from utils.py
from utils import (
    get_db_connection,
    prepare_results_file,
    get_key_words,
    execute_exact_match_queries,
    execute_misspelling_allowed_match_queries,
    RESULTS_FILE
)

@app.route('/enron-data/search', methods=['POST'])
def search():
    request_keys = request.json.get('key_words')
    if not request_keys or not isinstance(request_keys, str):
        return jsonify({'error': 'key_words is required and must be a string!'}), 400
    
    and_or_key_word_string, key_words_list = get_key_words(request_keys)

    print(f'request object: {request.json} || and_or_key_word_string: {and_or_key_word_string} || key_words_list: {key_words_list}')

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