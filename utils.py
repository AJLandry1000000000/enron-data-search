import psycopg2
import json
import os
import re

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

    # Remove commas from key_words (because they are going to be used later for the misspelling logic)
    key_words = key_words.replace(',', '')

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
        SELECT DISTINCT m.mid, m.sender, m.body, m.message_recipients, m.senders_most_common_recipient
        FROM message m
        WHERE to_tsvector('english', preprocessed_subject_and_body) @@ to_tsquery(%s);
    """
    
    cur.execute(query_string, (and_or_key_word_string,))

    insert_data_chunk(cur, match_type, and_or_key_word_string)

def execute_misspelling_allowed_match_queries(cur, key_words_list):
    match_type = 'misspelling_allowed_match' 

    for word in key_words_list:
        query_string = """
            SELECT DISTINCT m.mid, m.sender, m.body, m.message_recipients, m.senders_most_common_recipient
            FROM 
                message m
            INNER JOIN 
                preprocessed_text_single_words p ON m.mid = p.mid
            WHERE 
                similarity(p.word, %s) > %s
        """
        cur.execute(query_string, (word, SIMILARITY_THRESHOLD,))

        insert_data_chunk(cur, match_type, word)

def insert_data_chunk(cur, match_type, key_word):
    # Fetch and process results in chunks.
    current_chunk = 1
    current_records = 1
    while True:
        chunk = cur.fetchmany(CHUNK_SIZE)
        if not chunk:  # Break when no more rows to fetch.
            break
            
        print(f'{FILE_NAME} is processing "{match_type}" (chunk size {CHUNK_SIZE}) for keyword "{key_word}" | current chunk -> {current_chunk} | processing records -> {current_records} to {current_records + len(chunk)}')
        current_records += len(chunk)

        # Append each row as a standalone JSON object.
        with open(RESULTS_FILE, 'a') as json_file:
            for row in chunk:
                json_file.write(json.dumps({
                    "match_type": match_type,
                    "mid": row[0],
                    "sender": row[1],
                    "body": row[2],
                    "message_recipients": row[3],
                    "senders_most_common_recipient": row[4],
                }) + '\n')
        
        current_chunk += 1