"""
Implement model's featurization code in this class.
"""
from . import BaseModel


class Model(BaseModel):
    """
    Class for OfficeML Python models. Streamlines the workflow for testing and pushing models into production.
    """

    def __init__(self, data_dirpath=None):
        """
        Model constructor is used to create a representation of the Model associated with the
        data_dirpath argument and load other static files necessary for the deployment of the model.

        :param data_dirpath: The path of the directory where data for the model is stored.
        """
        super().__init__(data_dirpath)

{% if platform  != 'qas' %}
    def predict(self, data):
        """
        Predict a given value based on the trained model.

        :param data: Input value.
        :return: The model's predictions.
        """
        return 'Hello {}!'.format(data)
{% else %}

    def predict(self, analyzed_queries, modelName):
        """
        Predict a given value based on the trained model.

        :param data: raw_text_query, data type: string
        :return: The model's predictions, return type: string

        example: prediction = f(raw_text_query)
        """
        import QASOMLAPI
        raw_text_query = analyzed_queries[-1].Query.RawQuery
        prediction = 'hello world'

        string_segment = QASOMLAPI.CreateStringSegmentItem(
            segmentBeginIdx=0, segmentEndIdx=0, segmentFeatureId=1, value=prediction, weight=1)
        string_segment_list = QASOMLAPI.CreateStringSegmentItemList(string_segment)
        """
        can have multiple string_segment here
        string_segment_list.Add(string_segment2)

        Also, you can have multiple match_segment, featureSet, domain below

        match_segment_list.Add(match_segment2)
        featureset_list.Add(featureSet2)
        domain_list.Add(response_domain2)
        """

        match_segment = QASOMLAPI.CreateMatchSegmentItem(
            segmentBeginIdx=0, segmentEndIdx=0, segmentFeatureId=0, weight=1)
        match_segment_list = QASOMLAPI.CreateMatchSegmentItemList(match_segment)

        featureSet = QASOMLAPI.CreateFeaturizationOutput(
            featureSetName="featureSetName", match_segments=match_segment_list, string_segments=string_segment_list)
        featureset_list = QASOMLAPI.CreateFeaturizationOutputList(featureSet)

        response_domain = QASOMLAPI.CreateDomain(
            domainName=modelName, confidenceLevel=1.0, domainClassificationLevel=4, featurization_outputs=featureset_list)
        domain_list = QASOMLAPI.CreateDomainList(response_domain)

        aggregate_response = QASOMLAPI.CreateAggregateResponse(raw_text_query=raw_text_query, domains=domain_list)
        return aggregate_response
{% endif %}

    def eval(self, **kwargs):
        """
        Batch scoring on the trained model.

        :param kwargs: Extra parameters passed to the model.
        """
        self.generate_scores(0, 0)
