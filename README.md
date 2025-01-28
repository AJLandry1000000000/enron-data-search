# Enron email search application

FULL README COMING SOON!


## Task description


## Set-up commands
python3 -m venv python_env
source python_env/bin/activate
pip install Flask psycopg2-binary python-dotenv



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