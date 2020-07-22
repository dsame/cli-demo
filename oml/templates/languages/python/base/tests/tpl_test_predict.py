from unittest import TestCase

from .settings import PREDICTION_FILE_PATH
from {{namespace}}.model import Model
{% if platform  == 'qas' %}import QASOMLAPI{% endif %}

class PredictTest(TestCase):

    {% if platform  != 'qas' %}
    def test_predict(self):
        model = Model()
        with open(PREDICTION_FILE_PATH, 'r') as f:
            for row in f:
                data, expected = row.strip().split('\t')
                result = model.predict(data)

                self.assertEqual(result, expected)
    {% else %}
    def test_predict(self):
        model = Model()
        with open(PREDICTION_FILE_PATH, 'rb') as f:
            request_bytes = f.read()
        analyzed_queries = QASOMLAPI.Deserialize(request_bytes)
        aggregate_response = model.predict(analyzed_queries, "testqas")
        data = (aggregate_response.Responses[0].AnalyzedQueries)[0].Query.RawQuery
        self.assertEqual(data, "Suri is working on polymer project")
    {% endif %}
