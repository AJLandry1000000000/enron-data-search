# Enron email search application

FULL README COMING SOON!


## Task description


## Set-up commands
python3 -m venv python_env
source python_env/bin/activate
pip install Flask psycopg2-binary python-dotenv


NDJSON is used so file doesnt have to be loaded into memory to write to it. Additionally it is ideal for using the data since it can be read line by line, instead of having to be loaded all at once. 

WRITE ABOUT HOW THE USER MUST USE THE TABLE CREATION SQL FILES (enron_tables_psql.sql, enron_tables_index_adjustments_psql.sql) I HAVE BEFORE RUNNING THE PROJECT!


To see PG extensions...
SELECT * FROM pg_extension;

pg_trgm is a PostgreSQL extension that provides functions and operators for trigram-based text similarity matching. It is useful for approximate string matching, typo-tolerant searches, and fuzzy searching.

## How to use
First enter the python virtual environment with the following bash command:  
```source python_env/bin/activate```

Now run the application:  
```python find_keywords.py```  

Send a POST request to ```http://127.0.0.1:5000/enron-data/search```
Create a raw JSON body with key "key_words". Fill it with your key search word separates by: spaces for AND, and commas for OR.  
For example, if I wanted...  
```(milwaukee AND journal AND sentinel) OR (beautiful AND SUNDAY) OR (yellow)```  
then send the POST request with body:
```
{
    "key_words": "milwaukee journal sentinel, beautiful sunday, yellow"
}
```  


#### Notes
- API only allows one level AND/OR nesting. No multi-level.
- The search is case insensitive. 
- The search removes all white spaces beyond a single space. e.g. "A,           B" becomes "A, B"
- Removes all non-alphanumeric characters besides commas.
- 


## Further improvements

Add AND/OR functionality but allow for misspelling of the keywords. 
This is challenging with the current solution since to_tsquery() only supports exact matching of keywords in its syntax (though its syntax does allow AND/OR functionality). pg_trgm on the other hand allows misspelling, but does not support AND/OR functionality. Postgres does not have a built in ability to use AND/OR functionality with misspelling of keywords, so we would need to create a custom solution. 
The solution I have built uses AND/OR functionality for exact keyword matching (these records are identified by "match_type": "exact_match" in the results file), it also fetches records which misspell the keywords (but this logic doesn't use AND/OR functionality for those misspelled words. These potentially misspelled records are identified by "match_type": "misspelling_allowed_match" in the results file). 
An improvement would be to build AND/OR functionality but allow for misspelling of the keywords.

#### Note: records with AND/OR functionality and misspelling of the keywords is a subset of the records in our results file.
While I don't distinctly label records using AND/OR functionality with misspelled words, those records would be in our results file.
To explain lets define some terms:  

**possibly_misspelled** = records where keywords are potentially misspelled in the Enron emails. ("misspelling_allowed_match" records in the results file)  
**and_or_exact** = records adhering to the AND/OR logical operations of our input string, and keywords are exact matches to the Enron emails. ("exact_match" records in the results file)  
**and_or_possibly_misspelled** = records adhering to the AND/OR logical operations of our input string, and keywords are potentially misspelled in the Enron emails. <- labelling this set would be an improvement to our application!  

Since **possibly_misspelled** allows both exact and misspelled keyword matching, it is a super set of **and_or_exact** (i.e. **and_or_exact** is a subset of **possibly_misspelled**). But since **and_or_exact** is exact, by definition, misspelled words adhering to the AND/OR logical operators wont be in it's records.  
If we visualise a Venn diagram, **possibly_misspelled** contains sets **and_or_possibly_misspelled** and **and_or_exact**. So, **and_or_possibly_misspelled** is in our records file.  
More specifically, **and_or_possibly_misspelled** is in the set **possibly_misspelled** - **and_or_exact**.  
i.e. **and_or_possibly_misspelled** ⊆ (**possibly_misspelled** - **and_or_exact**)   ->   **and_or_possibly_misspelled** is a subset of, or equal to, the set (**possibly_misspelled** - **and_or_exact**)