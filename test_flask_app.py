import pytest
from celery import Celery

import flask_app


@pytest.fixture()
def client():
    client = flask_app.app.test_client()
    celery = Celery(flask_app.app.name)

    # setting this celery attribute to True, means tasks will be executed locally instead
    # of being sent to the queue.
    celery.conf.task_always_eager = True        # not sure this worked correctly
    return client


@pytest.fixture()
def source_tsv_file(tmpdir):
    """ Fixture creates a TSV source file with data.
    """
    tsv_file = tmpdir.mkdir('sub').join('open-food-facts_categories.tsv')
    tsv_file.write(
        'parent\tcategory\n'
        'Juices\tFruit juice\n'
        'Juices\tFruit juices\n'
        'Juices\tJuices\n'
        'Juices\tJuice\n'
        'Omelets\tEgg\'s omelet\n'
        'Eggs\teggs\n'
        'Dessert Wines\tfr:Sainte-croix-du-mont\n'
    )
    return str(tsv_file)


class TestAppEndpoints(object):

    def test_find_categories_for_query_where_no_text_parameter(self, client):
        response = client.get("/category/search?foo=bar")
        assert response.status_code == 400
        assert response.json == {'error': 'query string parameter text not found'}

    def test_find_categories_for_query_where_no_match_found(self, client):
        response = client.get("/category/search?text=foobar")
        assert response.status_code == 200
        assert response.json == {'message': 'no matches found'}

    def test_find_categories_for_query_with_valid_data_input(self, client):
        response = client.get("/category/search?text==I+wake+up+to+some+fruit+juices+and+eggs")
        assert response.status_code == 200
        assert response.json == {'categories_matched': ['Fruit juices', 'Eggs', 'juices']}

    def test_find_categories_for_query_where_edge_word_no_match(self, client):
        response = client.get("/category/search?text=I+have+egg+omelet")
        assert response.status_code == 200
        assert response.json == {'message': 'no matches found'}


class TestCeleryTaskFunctions(object):

    def test_search_for_matching_categories_removes_iso_code_from_output(self, source_tsv_file, monkeypatch):
        monkeypatch.setattr(flask_app, 'WORD_DICTIONARY_SOURCE', source_tsv_file)
        query_string = 'I+enjoy+sainte-croix-du-mont'
        outcome = flask_app.search_for_matching_categories(query_string)
        assert outcome == ['Sainte-croix-du-mont']
