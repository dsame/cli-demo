import os
from oml.hooks.graph import GraphHook


def get_pipeline_owner():
    email = os.environ.get('BUILD_REQUESTEDFOREMAIL') or os.environ.get('RELEASE_REQUESTEDFOREMAIL')
    if email is not None:
        graph = GraphHook()
        return graph.get_user_domain_alias(email)


def is_running_in_pipeline():
    pipeline_var = os.environ.get('BUILD_STAGINGDIRECTORY') or os.environ.get('RELEASE_RELEASEWEBURL')
    return pipeline_var is not None
