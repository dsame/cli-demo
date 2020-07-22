import os


BASE_TEST_PATH = os.path.dirname(__file__)
{% if platform  != 'qas' %}PREDICTION_FILE_PATH = os.path.join(BASE_TEST_PATH, 'predictions.txt')
{% else %}PREDICTION_FILE_PATH = os.path.join(BASE_TEST_PATH, 'test_requests.bin'){% endif %}
