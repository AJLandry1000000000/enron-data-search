# Enron email search application

# Table of Contents

1. [Introduction](#introduction)
2. [Task Description](#task-description)
3. [The Data](#the-data)
4. [The Tool](#the-tool)
5. [Input](#input)
6. [Output](#output)
7. [Constraints](#constraints)
8. [Tools and API](#tools-and-api)
   - [Tools](#tools)
   - [API](#api)
9. [Preprocessing, New Columns, and Indexing](#preprocessing-new-columns-and-indexing)
10. [Approach to Misspelling, AND/OR Operators, and Related Emails](#approach-to-misspelling-andor-operators-and-related-emails)
    - [AND/OR Operators](#andor-operators)
    - [Misspellings and Other Artifacts](#misspellings-and-other-artifacts)
    - [Related Email Data](#related-email-data)
11. [Further Improvements: AND/OR Operators on Misspelled Keywords](#further-improvements-andor-operators-on-misspelled-keywords)

## Task description
It's 2002. You are working as part of the US govt’s legal team on the Enron case, and you need to provide an efficient way to help the lawyers trawl through the email data to find relevant (incriminating) information.
 
### The data
There are a number of versions of the Enron data set: 
- SQL dump: [http://www.ahschulz.de/enron-email-data/](http://www.ahschulz.de/enron-email-data/) <- I chose this one!
- CSV flat file: [https://www.kaggle.com/datasets/wcukierski/enron-email-dataset](https://www.kaggle.com/datasets/wcukierski/enron-email-dataset)
- Flat MIME files: [https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz](https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz)  

Pick any version you feel lets you get started quickly.

### The tool
I created a quick-and-dirty REST API with one endpoint (using Python and Postgres). Send requests to  ```POST /enron-data/search```. It returns results sends data to a results file, ```results.ndjson```. 


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
(I won't give you a in-depth explanation since this can be figured out online)
Create your user and database. Make sure the database is running. Fill a .env file in your root repository with the database details. It should look something like this:
```
DB_NAME="your-database-name-here"
DB_USER="your-database-user-here"
DB_USER_PASSWORD="your-database-user-password-here" 
DB_HOST="localhost"
DB_PORT="your-database-port-here"
ENV="dev" # Change this to "prod" when running in production.
``` 
Next I downloaded the MySQL code from [here](http://www.ahschulz.de/enron-email-data/). Extract the SQL file. This file is full of table CREATE statements and INSERT statements. Remove all the CREATE statements (there are only 4), we will use the MySQL INSERT statements below. I have modified the tables for our application so use my table CREATE files. 
So run my modified sql CREATE files on your database with something like: 
```
psql -U your-database-user-here -d your-database-name-here -f pg_formated_files/enron_tables_psql.sql
psql -U your-database-user-here -d your-database-name-here -f pg_formated_files/enron_table_adjustments_psql.sql
```
Now you have your tables. Lets convert the MySQL INSERT file. Put it in the root directory, along with ```pg_formated_files/convert_mysql_to_pg.py```, and convert it to PSQL code using the following command:
```
python convert_mysql_to_pg.py 
```
Now load your new PSQL file into your Postgres database with:
```
psql -U your-database-user-here -d your-database-name-here -f enron-mysqldump-adjusted_psql.sql
```
Your database is now set up!
Note: there are lots of ways to convert the MySQL file into PostgreSQL code. e.g. you can use tools like ```pgloader``` and others...

Now that you are set up, start the python server with:
```
python find_keywords.py
```


## How to use & results explanation
First enter the python virtual environment with the following bash command (if you haven't already):  
```source python_env/bin/activate```

Start the the application:  
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
Results are sent to the ```results.ndjson``` file.
The results file has JSON objects with the following keys:
- **"match_type"**: the values can take the following
    - **"exact_match"**: meaning the email in that json object exactly matches the requirements of the AND/OR keyword string.
    - **"misspelling_allowed_match"**: meaning the email in that json object matched, or partially matched (mispelling), one of the keywords.
- **"mid"**: this is the message ID from the messages table.
- **"sender"**: this is the email sender's email.
- **"body"**: this is the body of the email which matched the keyword string.
- **"message_recipients"** : this is extra email information. It is a list of emails which the matching email was sent (i.e. the matching emails recipients).
- **"senders_most_common_recipient"**: this is extra email information. This email is the email (the email represented by the json object) senders most common email recipient.

#### Application use notes
- API only allows one level AND/OR nesting. No multi-level nesting.
- The search is case insensitive. 
- The search removes all white spaces beyond a single space. e.g. "A,         B" becomes "A, B"
- The search removes all non-alphanumeric characters (note commas and spaces are parsed before removal to implement the AND/OR operators explained above).


## Design choices

### Tools and API
I chose to use Python, because it's good with data, also I like it. :P 
I am using a Postrges database to leverage its native text search optimised function, ```to_tsquery()```, and a word similarity extension, ```pg_trgm``` (see definitions below). I also extensively used PSQL to optimise the database schema for our applications purposes.
I used an API solution, also because I like it. :P  
Results are sent to the ```results.ndjson```. A NDJSON results file is used so file doesnt have to be loaded into memory to write to it (due to the strict memory constraint, we can't load all the results data at once). Additionally, .ndjson files are ideal for the applications which use our results file sincee the data can be read line by line, instead of having to be loaded all at once (again, my solution was designed to assume we can't load all the results data at once). 

**pg_trgm** is a PostgreSQL extension that provides functions and operators for trigram-based text similarity matching. It is useful for approximate string matching, typo-tolerant searches, and fuzzy searching.  
**to_tsquery** is a powerful function in PostgreSQL that helps you convert a plain text query into a structured tsquery object, which can then be used to perform efficient full-text searches against tsvector data. It supports Boolean operators, making it flexible for complex search conditions.


### Preprocessing, new columns, and indexing
I indexed every column we were using for WHERE and JOIN statements. I also created some custom indexing for the tsquery column used in my text search (this special index column uses a GIN index), and for the pg_trgm column search (this special index column uses a GIN index and gin_trgm_ops. See the enron_table_adjustments_psql.sql file for more info). 

Since the database is unchanging, I could do lots of preprocessing without the challenge or reprocessing on data changes. This meant I could fill columns with preprocessed data to increase query time (since no subqueries or joins would be necessary if I preprocessed columns correctly). Here are some of new columns I added (in pg_formated_files/enron_table_adjustments_psql.sql) and filled with preprocessed data:
- **message.preprocessed_subject_and_body**: This column is a concatination of the subject and body columns in the message table. I then removed the "to: " and "cc: " email list, and removed HTML element (most of the "body" column is raw email/html). I also removed any base64 encoded strings, and removed extra white spaces (i.e. removed any spaces beyond 3 consecutive spaces). 
- **message.preprocessed_subject_and_body**: This new preprocessed_subject_and_body served as the bases of our "search vector" which would be converted to tsquery type so our application could use the ```to_tsquery()``` function for AND/OR word searching.
- **message.senders_most_common_recipient**: This is a "related emails" column. senders_most_common_recipient tracks the email senders most common point of contact. I filled this column with a one time INSERT statement using a subquery that would have been far to expensive to run every time we fetched this information.
- **message.message_recipients**: This is another "related emails" column. This is a colume which aggregates data from the "recipientinfo" table (which would have been too slow to compute as a subquery at runtime). It tracks the email's list of recipients.

I also created a new table called **preprocessed_text_single_words** which contains single words from every message's preprocessed_subject_and_body column. It was then indexed with the special pg_trgm index for fast misspelling string search.


### Approach to data loading: chunking and output file
Since I was under the constraint of limited memory, I built my entire application assuming we could not store the entire results of our database queries in memory.  
To address this issue I used the python code ```cur.fetchmany(CHUNK_SIZE)``` to fetch the results of our query incrementally, never loading them all in at once (for my application, ```CHUNK_SIZE=1000```, but you could change this depending on your machine). The code then appends our results file (the file is cleared beforehand so the file only contains results of the last ```/enron-data/search``` request) each of these records, with some metadata to a results file ```results.ndjson``` (see the [Tools and API](#tools-and-api) section for more details).  
Because we are under such a memory constraint, I decided to incrementally append to a file, so that the results didn't have to be stored in memory, as would have been required if we wanted to return the results to the API request.

### Approach to misspelling, AND/OR operators, and related emails
**AND/OR operators**: I used tsquery syntax with the ```to_tsquery()``` function to implement this functionality. The new preprocessed_subject_and_body served as the bases of our "search_vector" column which would take preprocessed_subject_and_body and convert it to tsquery type. After indexing the search_vector column with the special GIN index, our application could query the search_vector using AND/OR logical word searching.  
See the code for this functionality in ```utils.py -> execute_exact_match_queries()```.

**Misspellings and other artifacts**: The "misspellings and other artifacts" input constraint was implemented using the Postgres pg_trgm extension (see the [Tools and API](#tools-and-api) section for more details). I moved the preprocessed message body column (preprocessed_subject_and_body) into a new table, preprocessed_text_single_words, which contained message ID and the seperated out words from message.preprocessed_subject_and_body (tokenised by spaces). I then used the special GIN pg_trgm index to improve the search time of the pg_trgm tool.  

See the code for this functionality in ```utils.py -> execute_misspelling_allowed_match_queries()```. My misspelling query in ```execute_misspelling_allowed_match_queries()```, function uses a similarity() function which measures how close a word is, to our (potentially) misspelled keyword. I used a similarity threshold of 0.6 since my online research, and testing, indicated that 0.6 allowed 1-2 incorrect characters between the keyword and the comparison word. To increase or decrease the similarity precision, change the ```SIMILARITY_THRESHOLD``` variable in ```utils.py```.

**Related email data**: The extra "related" emails returned with our matching emails contained related emails such as, the emails recipients, and the senders most common email contact (see the [Preprocessing, new columns, and indexing](#preprocessing-new-columns-and-indexing) section for more info).  
Both of these columns were prefilled with a subquery so they did not have to be computed at runtime (that would have dramatically decreased performance).


## Further improvements: AND/OR operators on misspelled keywords.
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

## Further improvements: Testing suite
Implement unit tests, integration tests, and performance tests to ensure the tool works as expected. Use frameworks like pytest and locust.

## Futher improvements: UX
The following features could expland our application and make its use easier:
- Allow users to filter by date range, sender, or recipient.
- Allow a NOT keyword in addition to our AND/OR functionality.
- Allow users to customise the output file (e.g. change the file type, what kind of match_type they want, change the "related" emails metrics, etc)
- Allow users to search for phrases in additon to individual keywords. e.g. phrases could be wrapped in "" marks.

## Further improvements: Advanced search options
**Sentiment Analysis**: For really complex improvements you could use a model trained in Sentiment Analysis. In the context of the Enron email dataset, this can help prioritize emails that exhibit strong emotions (e.g., anger, urgency, or frustration), which might indicate incriminating or important content. The sentiment model could give every message a sentiment_score. This could allow users to filter emails by sentiment (e.g., "show me angry emails").

**Graph database**: Use a graph database like Amazon Neptune to analyze relationships between emails, senders, and recipients. A graph database could:
- Identify clusters of related emails. e.g. identify email threads shared between a small subnetwork of employees (this could lead to discovering organised criminal activity).
- Efficiently answer very complex "connection" type questions. e.g. find emails with keyword "**keyword_1**". What were the emailers top 10 contacts during the month after that matching email? also for those top 10 contacts, in the following month after the matching email, what were their most contacted emails with "President" or "Director" type employees? Who did those "President" or "Director" type employees email with keyword "**keyword_2**"?
- Visualize email threads and communication patterns.

## Further improvements: Other tools
**Asynchronous Processing with Redis or ElastiCache**: Asynchronous processing would allow you to offload time-consuming tasks, such as large search requests, to background workers. This ensures our application remains responsive.  
**Elasticsearch**: Elasticsearch is a distributed search engine designed for fast, scalable full-text search. It’s ideal for handling large datasets like the Enron emails.  
**Caching**: Use caches such as Redis or ElastiCache to store frequently accessed data in memory to reduce database load and improve response times.