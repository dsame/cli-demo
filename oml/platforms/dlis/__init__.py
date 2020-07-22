import os

from oml.exceptions import OMLException
from oml.hooks.dlis import DLISHook
from oml.hooks.catalog import ModelCatalogHook
from oml.settings import (
    find_base_path,
    load_model_metadata,
    TEST_JOB_TYPE,
    DEPLOYMENT_JOB_TYPE,
    PYTHON_LANG,
    CSHARP_LANG)
from oml.util import pipeline
from oml.util.os import get_user


class DlisApi:

    def __init__(self):
        try:
            self.base_path = find_base_path(os.getcwd())
            self.metadata = load_model_metadata(self.base_path)
        except Exception:
            self.metadata = None
        self.client = DLISHook()
        self.catalog = ModelCatalogHook(self.metadata)

    def get(self, resource, job_id=None):
        result = None
        filters = {}

        if job_id is None:
            model = self._get_model_info()
            filters['ModelName'] = model['name']
            filters['DRI'] = model['owner'].split('\\')[1]
        if resource == TEST_JOB_TYPE:
            result = self.client.get_tests(id=job_id, filter=filters)
        elif resource == DEPLOYMENT_JOB_TYPE:
            result = self.client.get_deployments(id=job_id, filter=filters)

        if result is not None:
            if job_id is None and len(result) > 0:
                result = result[0]
            if 'Status' in result:
                self.catalog.update_deployment(job_id, result['Status'].lower())
        return result

    def list(self, resource, model_name=None, owner=None, status=None):
        jobs = []
        filters = {}

        model = self._get_model_info(model_name)
        if model_name is not None:
            filters['ModelName'] = model_name
        elif owner is not None:
            filters['Owner'] = owner
        elif status is not None:
            filters['ModelName'] = model['name']
            filters['Status'] = status
        else:
            filters['ModelName'] = model['name']
            filters['DRI'] = model['owner'].split('\\')[1]

        if resource == TEST_JOB_TYPE:
            result = self.client.get_tests(filter=filters)
        elif resource == DEPLOYMENT_JOB_TYPE:
            result = self.client.get_deployments(filter=filters)

        if result is None:
            return None
        for p in result:
            jobs.append({
                'id': p['ID'],
                'model_name': p['ModelName'],
                'start_time': p['StartTime'],
                'end_time': p['EndTime'],
                'status': p['Status'],
                'namespace': p['Namespace'] if 'Namespace' in p else None,
                'is_compliant': p['IsCompliant'] if 'IsCompliant' in p else None,
                'error': p['Error'] if p['Error'] is None else '{}...'.format(p['Error'][:50])
            })
            self.catalog.update_deployment(p['ID'], p['Status'].lower())
        return jobs

    def _get_configuration(self, command):
        """Get custom default configs from oml.yml file."""
        if ('commands' in self.metadata and 'dlis' in self.metadata['commands']
                and command in self.metadata['commands']['dlis']):
            return self.metadata['commands']['dlis'][command]

        return {}

    def _get_model_settings(
            self,
            config,
            timeout_in_ms,
            max_query_size_in_bytes,
            waiting_model_ready_in_min,
            cpu_cores,
            memory_usage_in_mb,
            gpu_devices,
            fpga_devices,
            use_avx2,
            environment_vars):
        return {
            'TimeoutInMs': timeout_in_ms or config.get('timeout-in-ms', 100),
            'MaxQuerySizeInBytes': max_query_size_in_bytes or config.get('max-query-size-in-bytes', 65536),
            'WaitingModelReadyInMin': waiting_model_ready_in_min or config.get('waiting-model-ready-in-min', 10),
            'ModelResourceConstraint': {
                'MaxPhysicalCpuCores': cpu_cores or config.get('cpu-cores', 2),
                'MaxMemoryUsageInMB': memory_usage_in_mb or config.get('memory-usage-in-mb', 2048),
                'MaxGpuDevices': gpu_devices or config.get('gpu-devices', 0),
                'MaxFpgaDevices': fpga_devices or config.get('fpga-devices', 0),
                'NeedsAvx2': use_avx2 or config.get('use-avx2', False)
            },
            'EnvironmentVars': self._get_env_vars_list(environment_vars, config.get('env-vars', None))
        }

    def _get_env_vars_list(self, cmd_env_vars, config_env_vars):
        env_vars_dict = {
            'KMP_AFFINITY': 'respect,none',
            'PYTHONUNBUFFERED': '1'
        }
        # convert each list to a tuple and add to dict. if value exists, overwrite
        # values in config file will overwrite defaults above
        # values passed in the command will overwrite config and default values
        if config_env_vars is not None:
            config_pairs = [env_var.split('=') for env_var in config_env_vars.split(';')]
            env_vars_dict.update(config_pairs)
        if cmd_env_vars is not None:
            cmd_pairs = [env_var.split('=') for env_var in cmd_env_vars.split(';')]
            env_vars_dict.update(cmd_pairs)

        # convert dict to list and return
        return ['{}={}'.format(name, value) for name, value in env_vars_dict.items()]

    def _get_owner(self):
        if self._pipeline_is_running():
            owner = pipeline.get_pipeline_owner()
            if owner is None:
                raise OMLException("Can't find user email or alias.")
            return owner
        else:
            return get_user()

    def _pipeline_is_running(self):
        return os.environ.get('OML_CLI_KEY') is not None

    def test(
            self,
            model_name=None,
            model_version=None,
            model_type=None,
            artifact_uri=None,
            test_query_uri=None,
            platform_type='Windows',
            timeout_in_ms=None,
            max_query_size_in_bytes=None,
            qps=None,
            environment_vars=None,
            waiting_model_ready_in_min=None,
            cpu_cores=None,
            memory_usage_in_mb=None,
            gpu_devices=None,
            fpga_devices=None,
            use_avx2=None):
        model = self._get_model_info(model_name, model_version)
        artifacts = self.catalog.get_model_artifacts(model_id=model['id'], is_compliant=False, version=model_version)
        if len(artifacts) == 0:
            raise OMLException("""Please publish the model before testing it.
            If you specified a version, check that the version was published.
            You can run "oml list" to see the published versions.""")
        artifact = artifacts[0]

        if model_type is None:
            if model['language'] == CSHARP_LANG:
                model_type = 'WindowsLibrary'
            elif model['language'] == PYTHON_LANG:
                model_type = 'WindowsProcess'
            else:
                raise OMLException('Language is not supported: {}'.format(model['language']))
        if artifact_uri is None:
            artifact_uri = artifact['path']
        if test_query_uri is None:
            test_query_uri = '{}model/data/input.txt'.format(artifact_uri)

        config = self._get_configuration('test')
        data = self._get_model_settings(
            config,
            timeout_in_ms,
            max_query_size_in_bytes,
            waiting_model_ready_in_min,
            cpu_cores,
            memory_usage_in_mb,
            gpu_devices,
            fpga_devices,
            use_avx2,
            environment_vars)

        data.update({
            'Owner': self._get_owner(),
            'DRI': model['owner'].split('\\')[1],
            'ModelName': model['name'],
            'ModelType': model_type,
            'PlatformType': platform_type,
            'QPS': qps or config.get('qps', -1),
        })

        if model['language'] == CSHARP_LANG:
            sub_data = {
                'ModelDll': '{}Inference.dll'.format(model['name']),
                'ModelClassName': '{}.{}Inference'.format(model['name'], model['name']),
                'ModelPath': {
                    'CosmosPath': artifact_uri
                },
                'TestQuery': '{}data/input.txt'.format(artifact_uri)
            }
        elif model['language'] == PYTHON_LANG:
            sub_data = {
                'CmdAndArgs': ['run.cmd'],
                'ModelPath': {
                    'CosmosPath': '{}model/run.cmd'.format(artifact_uri)
                },
                'CondaPath': {
                    'CosmosPath': '{}conda/{}.zip'.format(artifact_uri, model['name'])
                },
                'TestQuery': '{}model/data/input.txt'.format(artifact_uri)
            }
        else:
            raise OMLException('Language is not supported: {}'.format(model['language']))
        data.update(sub_data)

        job_id = self.client.create_test(data)
        self.catalog.create_deployment(artifact['id'], job_id, TEST_JOB_TYPE)
        return job_id

    def deploy(
            self,
            model_type=None,
            model_name=None,
            custom_model_name=None,
            model_version=None,
            namespace=None,
            platform_type=None,
            environments=None,
            environment_vars=None,
            parallelism=None,
            instances=None,
            is_compliant=None,
            compliant_acl_allow=None,
            max_query_size_in_bytes=None,
            timeout_in_ms=None,
            waiting_model_ready_in_min=None,
            cpu_cores=None,
            memory_usage_in_mb=None,
            gpu_devices=None,
            fpga_devices=None,
            use_avx2=None,
            force_replace=None,
            replace_version=None):
        if self.metadata is None and model_name is None:
            raise OMLException('Please provide model name.')
        model = self._get_model_info(model_name, is_compliant, model_version)

        artifacts = self.catalog.get_model_artifacts(model['id'], is_compliant=is_compliant, version=model_version)
        if len(artifacts) == 0:
            raise OMLException("""Please publish the model before deploying it.
            If you specified a version, check that the version was published.
            You can run "oml list" to see the published versions.""")

        artifact = artifacts[0]
        artifact_uri = artifact['path']
        tests = self.catalog.get_model_tests(artifact['id'])

        if is_compliant is None:
            is_compliant = artifact['is_compliant']

        if not is_compliant:
            if len(tests) > 0:
                test_id = tests[0]['job_id']
                test = self.client.get_tests(id=test_id)
                if test is None or test['Status'] != 'Succeeded':
                    raise OMLException('Please pass the Polaris test before deploying the model.')
            else:
                raise OMLException('Please pass the Polaris test before deploying the model.')

        if is_compliant and compliant_acl_allow is None:
            raise OMLException('Please assign --compliant-acl-allow (-t) with certificate thumbprint(s).')

        if model_type is None:
            if model['language'] == CSHARP_LANG:
                model_type = 'WindowsLibrary'
            elif model['language'] == PYTHON_LANG:
                model_type = 'WindowsProcess'
            else:
                raise OMLException('Language is not supported: {}'.format(model['language']))

        if custom_model_name is not None:
            model_name = custom_model_name
        else:
            model_name = model['name']

        config = self._get_configuration('deploy')
        data = self._get_model_settings(
            config,
            timeout_in_ms,
            max_query_size_in_bytes,
            waiting_model_ready_in_min,
            cpu_cores,
            memory_usage_in_mb,
            gpu_devices,
            fpga_devices,
            use_avx2,
            environment_vars)

        namespace = namespace or config.get('namespace')
        instances = instances or config.get('instances', 1)

        if namespace is None:
            raise OMLException('Namespace is required to deploy. Add default in oml.yml or provide as option.')

        instances_list = self._get_instances_per_environment(instances, environments)

        environments_list = []
        for i, environment in enumerate(environments.split(';')):
            environments_list.append({
                'Environment': environment,
                'MinInstanceNum': instances_list[i],
                'MaxInstanceNum': instances_list[i]
            })
        data.update({
            'Owner': self._get_owner(),
            'DRI': model['owner'].split('\\')[1],
            'Namespace': namespace,
            'ModelName': model_name,
            'ModelType': model_type,
            'Parallelism': parallelism or config.get('parallelism', 1),
            'PlatformType': platform_type or 'Windows',
            'Environments': environments_list,
        })

        if model['language'] == CSHARP_LANG:
            if is_compliant:
                model_uri = artifact_uri.strip("/")
            else:
                model_uri = artifact_uri
            sub_data = {
                'ModelDll': '{}Inference.dll'.format(model['name']),
                'ModelClassName': '{}.{}Inference'.format(model['name'], model['name']),
            }
        elif model['language'] == PYTHON_LANG:
            model_uri = '{}model/run.cmd'.format(artifact_uri)
            if is_compliant:
                storage = 'AzurePath'
            else:
                storage = 'CosmosPath'
            sub_data = {
                'CmdAndArgs': ['run.cmd'],
                'CondaPath': {
                    storage: '{}conda/{}.zip'.format(artifact_uri, model['name'])
                }
            }
        else:
            raise OMLException('Language is not supported: {}'.format(model['language']))
        data.update(sub_data)

        if not is_compliant:
            data.update({
                'TestID': test_id,
                'ModelPath': {
                    'CosmosPath': model_uri
                },
            })
            if compliant_acl_allow is not None:
                data.update({
                    'CompliantAclAllow': compliant_acl_allow
                })

        if is_compliant:
            data.update({
                'IsCompliant': is_compliant,
                'CompliantAclAllow': compliant_acl_allow,
                'ModelPath': {
                    'AzurePath': model_uri
                },
            })

        replace_flag = {
            'AllocationSettings': {
                'ModelVersionToReplace': replace_version or "true"
            }
        }
        # if force replace flag is present, use it to evaluate whether to add or not
        if force_replace is not None:
            if force_replace:
                data.update(replace_flag)
        else:
            # if there is an active model already, add Replace flag
            # for non-comp, only add flag when there is an active model running in any of the environments to deploy.
            active_models = self.client.get_active_models(namespace=namespace, name=model_name)
            if active_models is not None and len(active_models) > 0:
                if is_compliant:
                    data.update(replace_flag)
                else:
                    for model in active_models:
                        if model["Deployments"][0]["Environment"] in environments:
                            data.update(replace_flag)
                            break

        job_id = self.client.create_deployment(data)
        self.catalog.create_deployment(artifact['id'], job_id, DEPLOYMENT_JOB_TYPE)
        return job_id

    def _get_model_info(self, name=None, is_compliant=None, version=None):
        if self.metadata is None and name is None:
            raise OMLException('Please provide model name.')
        if name is None:
            name = self.metadata['name']
        model = self.catalog.get_model(name)
        if model is None:
            raise OMLException('Model not found. Please check that you have published your model.')
        return model

    def _get_instances_per_environment(self, instances, environments):
        environments_count = len(environments.split(';'))
        instances_list = str(instances).split(';')
        if len(instances_list) == 1:
            instances_list = [instances] * environments_count
        elif len(instances_list) != environments_count:
            raise OMLException('Instances count does not match environments count. '
            'Please provide either one value to use in all environments, or one value per environment.')
        return instances_list
