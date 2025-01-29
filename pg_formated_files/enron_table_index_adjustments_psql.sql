ALTER TABLE message ADD COLUMN search_vector tsvector;

ALTER TABLE message ADD COLUMN preprocessed_subject_and_body text; -- Removed the HTML code and base64 encoded data from the body column.

CREATE INDEX idx_search_vector ON message USING GIN(search_vector);

UPDATE message
SET preprocessed_subject_and_body = lower( -- make the whole column lowercase so it is case insensitive for our input string.
    regexp_replace(
        regexp_replace(
            regexp_replace(
                regexp_replace(
                    coalesce(subject, '') || ' ' || coalesce(body, ''),
                    '(?i)(to:|cc:)\s[^,]*(,[^,]*)*',  -- Match the To: or CC: list (case insensitive)
                    '',
                    'g'
                ),
                '<[^>]*>',  -- Remove HTML tags
                '',
                'g'
            ),
            '[A-Za-z0-9+/=]{100,}',  -- Remove long (100 characters or more) base64-like sequences
            '',
            'g'
        ),
        '\s{4,}',  -- Replace sequences of 4 or more spaces with exactly 3 spaces
        '   ',
        'g'
    )
);

UPDATE message SET search_vector = to_tsvector('english', preprocessed_subject_and_body); 



CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX idx_preprocessed_subject_and_body_similarity ON message USING GIN (preprocessed_subject_and_body gin_trgm_ops);


-- Create the preprocessed_text_single_words table
CREATE TABLE preprocessed_text_single_words (
    id SERIAL PRIMARY KEY,
    mid INT REFERENCES message(mid),
    word TEXT
);

-- Populate the preprocessed_text_single_words table
INSERT INTO preprocessed_text_single_words (mid, word)
SELECT 
    mid, 
    regexp_split_to_table(preprocessed_subject_and_body, '\s+') AS word
FROM message;

-- Add indexes.
-- GIN index for pg_trgm similarity
CREATE INDEX idx_word_similarity ON preprocessed_text_single_words USING GIN (word gin_trgm_ops);
-- Index on mid for faster joins
CREATE INDEX idx_preprocessed_text_single_words_mid ON preprocessed_text_single_words(mid);
CREATE INDEX idx_preprocessed_text_single_words_word ON preprocessed_text_single_words(word);

-- Optional: Add a composite index
CREATE INDEX idx_preprocessed_text_single_words_mid_word ON preprocessed_text_single_words(mid, word);



