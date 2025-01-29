# Enron email search application

## Task description
It's 2002. You are working as part of the US govt’s legal team on the Enron case, and you need to provide an efficient way to help the lawyers trawl through the email data to find relevant (incriminating) information.
 
### The data
There are a number of versions of the Enron data set: 
- SQL dump: [http://www.ahschulz.de/enron-email-data/](http://www.ahschulz.de/enron-email-data/) <- I chose this one!
- CSV flat file: [https://www.kaggle.com/datasets/wcukierski/enron-email-dataset](https://www.kaggle.com/datasets/wcukierski/enron-email-dataset)
- Flat MIME files: [https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz](https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz)
Pick any version you feel lets you get started quickly.

### The tool
I created a quick-and-dirty REST API with one endpoint. Send requests to  ```POST /enron-data/search```. It returns results sends data to a results file, ```results.ndjson```. 
I created this with Python and a PostgreSQL database. Results are sent to the ```results.ndjson```. An NDJSON results file is used so file doesnt have to be loaded into memory to write to it (due to the strict memory constraint, we can't load all the results data at once). Additionally, .ndjson files are ideal for the applications which use our results file sincee the data can be read line by line, instead of having to be loaded all at once (again, my solution was designed to assume we can't load all the results data at once). 

### Input
A string containing a list of keywords to search for. The keywords can include misspellings and other artifacts, and can be specified in any order.
For bonus points, you should allow keywords to be logically grouped via and/or operators.

### Output
A list of matching emails, referenced by their ID or file name, depending on the data set, plus the matched email text.
 
For bonus points, include emails that do not match the search query but instead are *related* by some metric to any email returned by the search query or the search query itself.

In my assignment I returned some additional data per email, this includes a list of all the emails recipients (see ```"message_recipients"``` in ```results.ndjson```) and the email senders most common point of contact (see ```"senders_most_common_recipient"``` in ```results.ndjson```).

### Constraints
- You can use a language and runtime of your choice (we speak Java, Kotlin, C/C++, Python, C#).
- You can preprocess the data and use a storage/indexing mechanism of your choice.
- You are permitted to leverage any database indexing and free-text search mechanism you like.
- Your tool must be able to be run within tight memory constraints (e.g. -Xmx256m in Java), effectively meaning you cannot load all the data into memory at once.

### What we want to see
- Even though this is a time-constrained task, we want to see evidence of your ability to clearly structure and architect your code.
- We want to see evidence you have considered common issues that come into play with handling, indexing and searching a large body of unstructured text and some commentary as to what they are.
- While you won’t necessarily have the time to produce a truly performant solution, we want to see reasonable performance from the tool.
- Consider and comment how you would architect the tool to work over a much larger data set – gigabytes or petabytes of data.
- We want to see some commentary on your implementation and what you would improve if you were given more time to complete the task.



## Set-up commands
Once you have cloned the git repostory, navigate to the root directory of the project and run the following commands to create the python virtual environment, start the virtual enviroment, and install the necessary python packages.
```
python3 -m venv python_env
source python_env/bin/activate
pip install Flask psycopg2-binary python-dotenv
```
Next you will need to load all the SQL data to create the tables.







WRITE ABOUT HOW THE USER MUST USE THE TABLE CREATION SQL FILES (enron_tables_psql.sql, enron_tables_index_adjustments_psql.sql) I HAVE BEFORE RUNNING THE PROJECT!


To see PG extensions...
SELECT * FROM pg_extension;

pg_trgm is a PostgreSQL extension that provides functions and operators for trigram-based text similarity matching. It is useful for approximate string matching, typo-tolerant searches, and fuzzy searching.

## How to use
First enter the python virtual environment with the following bash command (if you haven't already):  
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
- The search removes all white spaces beyond a single space. e.g. "A,         B" becomes "A, B"
- Removes all non-alphanumeric characters besides commas.
- 
the new columns message_recipients and most_common_recipient are prefilled so no subqueries are necessary (too slow).

## Design choices

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