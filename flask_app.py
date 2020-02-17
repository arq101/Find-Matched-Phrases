# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from celery import Celery
import re
import pandas

WORD_DICTIONARY_SOURCE = './data_source_open_food_facts/off_categories.tsv'


app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)
# configure Celery instance with the broker from the Flask app config
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


@app.route('/category/search', methods=['GET'])
def find_categories_for_query():
    query_string = request.args.get('text')
    if query_string:
        matches_found = search_for_matching_categories.apply_async(args=[query_string])
        # matches_found = search_for_matching_categories(query_string)        # for debugging
        result = matches_found.wait()
        if result:
            return jsonify({'categories_matched': result})
        else:
            return jsonify({'message': 'no matches found'})
    else:
        return jsonify({'error': 'query string parameter text not found'}), 400


@celery.task
def search_for_matching_categories(query_string):
    # read TSV data file as a dataframe object, discarding all other columns at parse time
    df_categories = pandas.read_csv(WORD_DICTIONARY_SOURCE, delimiter='\t', usecols=['category'])

    # iso_pattern for 2 or 3 letter country ISO codes
    iso_pattern = re.compile(r'^\w{2,3}:', flags=re.IGNORECASE)

    # remove iso codes prefixing the category phrases for non-english languages
    categories = df_categories['category'].str.replace(iso_pattern, '')     # pandas Series object
    categories = categories.dropna().unique()                       # get ndarray of unique values

    matches_found = []
    for phrase in categories:
        if re.search(r'\b{}\b'.format(phrase), query_string, re.IGNORECASE):
            matches_found.append(phrase)
    return matches_found


if __name__ == '__main__':
    app.run(debug=True, port=8080)
