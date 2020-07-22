"""
Implement model's featurization code in this class.
"""
from .nlx_model import NLXModel


class Model(NLXModel):

    def __init__(self, data_dirpath=None):
        """
        Load model(s) and other static files.
        """
        super().__init__(data_dirpath)

    def predict(self, data):
        """
        Predict a given value based on the trained model.

        :param data: Input value.
        :return: The model's predictions.
        """
        return 'Hello {}!'.format(data)

    def eval(self, **kwargs):
        """
        Batch scoring on the trained model.

        :param kwargs: Extra parameters passed to the model.
        """
        self.generate_scores(0, 0)
