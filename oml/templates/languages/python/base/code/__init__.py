"""
===========
DO NOT EDIT
===========

Base abstract class for OXO models.

The class is auto-generated from saved template. Implement your
featurization code in Model class that extends this base class.
"""
from abc import ABC, abstractmethod
from os.path import abspath, dirname, join
from .settings import SCORE_FILE_NAME


class BaseModel(ABC):

    def __init__(self, data_dirpath):
        self.base_path = abspath(join(dirname(__file__), '..'))
        self.data_dirpath = join(self.base_path, 'data') if data_dirpath is None else data_dirpath
        self.model_dirpath = join(self.data_dirpath, 'model')

    @abstractmethod
    def predict(self, data):
        pass

    @abstractmethod
    def eval(self, **kwargs):
        pass

    def generate_scores(self, precision, recall):
        """
        Generate .score file and print the scores.

        :param precision: Model precision value.
        :param recall: Model recall value.
        """
        with open(join(self.base_path, SCORE_FILE_NAME), 'w') as f:
            f.write('precision: {}\n'.format(precision))
            f.write('recall: {}'.format(precision))

        print('----------------------- Result -----------------------')
        print('  Precision: {}'.format(precision))
        print('  Recall: {}'.format(recall))
        print('------------------------------------------------------')
