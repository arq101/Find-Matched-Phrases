# Data Processing Of Matched Phrases

A micro-service that takes as input a string parameter containing natural language in any relevant language, and returns a list of matched phrases from a dictionary list independent of case and plurality and punctuation.

The test dictionary of phrases is called `off_categories.tsv` The second column, called 'category' is the column to look for (it is the categories from Open Food Facts) . The category names may be plural or singular (OFF is a crowdsourced categorisation, so is not entirely consistent), but the matches should be found either way. Some categories are in non-English language, signified by an ISO language code and colon which needs to be removed for matches to be possible.

## Example input and output (logical):

Input: ```I like lemon juice and granulated sugar on my pancakes.```

Output: ```[ "Lemon juice", "Granulated sugars", "Pancakes" ]```

Note that this input should not match other phrases from the phrases list that have the word `juice` or `sugar` in them uf the rest of those categories are not matched with this input.

## Interface

The micro-service should listen on port 8080, and should accept the input as a querystring parameter called `text`

## Requirements

* Use appropriate production-capable frameworks
* Use appropriate dependency-management and build tools
* The project's structure and organization should follow best practices
* Don't reimplement the wheel, reuse
* Prefer immutable design if possible
* Performance matters. Consider your chosen algorithm, its throughput, scalability, memory-usage
* If the framework you use is single-threaded by default, you may want to provide a multi-threaded version also
* Test your code, and your API. No need to test every permutation, but demonstrate you know the types of things to test for.
* Even though this is a simplified requirement as appropriate to being an exercise, your code should be production capable
* Show your working, if you've used any interesting libraries or approaches during development let us know and explain why in the readme. 


## Problems & Limitations Encountered And Further Improvements
1) The data found in the food category phrases list is dirty.  
ie. it is not consistent, too many variants of essentially the same category, and some garbage entries.  

Which meant that when searching for English word plurals, my regex expression was matching on nonsensical characters. Therefore I had to go for an exact word match, resulting in some plurals not being found by the search. Hence, it needs improving.

2) If one provides a query string containing ```fruit juices```, the interface will match for both ```Fruit juices``` and ```juices```, because these are both phrases that currently exist in the Open-Food-Facts category listing.
  
3) Currently the matching of food categories for non-ASCII characters in the query strings is not working.  

Accessing the query string in the view function using Flask request, shows the words with non-ASCII characters to be encoded in something other than UTF-8.    

Need to do look into this further.

4) Further improvement in case the size of the source file became very large, would be to have the categories of foods stored in a database table.

5) Another improvement, when it comes to doing the actual search, maybe to look at a binary search library such as bisect.

## Start Message Broker: Redis
If Redis is already installed locally, start Redis by running ...
```
sudo systemctl start redis 
```
  
Alternatively, run Redis as a container
```
docker run -d -p 6379:6379 redis
```

## Set up virtualenv with Python 3.7

Assuming virtualenv is already installed on your system.  
If using a virtualenvwrapper then set up a virtual environment for this project   
eg.
```
mkvirtualenv -p /usr/bin/python3.7 -a [path to project] [virtualenv name]
```
Otherwise set up your virtual environment as you normally would.  

Once your virtualenv is active in the terminal, install the necessary dependencies
```
pip3 install -r requirements.txt
```


## Unit-testing
In a new terminal with virtualenv active, run unit tests ...  
NOTE: requires Redis and Celery to be running (did not get time to correctly set the unittests to run synchronously)
```
pytest -v test_flask_app.py
```


## Start the Flask application
From a terminal with virtualenv active, start the app by running  
```
python flask_app.py
```

## Start the Celery worker
From another terminal with virtualenv active, start a single instance of a celery worker
```
celery worker -A flask_app.celery --loglevel=info
```


## Test the micro-service interface
In a terminal pass the following query strings to the interface endpoint
- I wake up to some fruit juices and eggs
- I like lemon juice and granulated sugar on my pancakes.
- Endives en conserve dans ma salade
  
NOTE: space characters are not allowed in a URL, so they must be replaced with + or %20 in the query string.  
eg.
```
curl -i "localhost:8080/category/search?text=I+wake+up+to+some+fruit+juices+and+eggs"
```
```
curl -i "localhost:8080/category/search?text=I+like+lemon+juice+and+granulated+sugar+on+my+pancakes."
```
```
curl -i "localhost:8080/category/search?text=endives+en+conserve+dans+ma+salade"
```
Alternatively run the 3 requests in a web-browser by going to:  
```localhost:8080/category/search?text=I+wake+up+to+some+fruit+juices+and+eggs```  
```localhost:8080/category/search?text=I+like+lemon+juice+and+granulated+sugar+on+my+pancakes.```  
```localhost:8080/category/search?text=endives+en+conserve+dans+ma+salade```  
  
  
Outcomes respectively ...
```
{
  "categories_matched": [
    "Fruit juices", 
    "Eggs", 
    "juices"
  ]
}
```
```
{
  "categories_matched": [
    "Lemon juice", 
    "Pancakes", 
    "juice"
  ]
}
```
```
{
  "categories_matched": [
    "Endives en conserve", 
    "Endives"
  ]
}
```
