import json

from cappy import API

class Project(object):

    def __init__(self, endpoint, token, is_super_token=True):
        self.cappy_super_version = 'v6.16.0.redi_ready.json'
        self.cappy_api_version = 'master.yaml'
        self.endpoint = endpoint
        if is_super_token:
            self._super_api = API(token, endpoint, self.cappy_super_version)
            self.super_token = token
        else:
            self._api = API(token, endpoint, self.cappy_api_version)
            self.token = token

    def create_project(self, project_csv, is_longitudinal=True):
        """
        Used to create a new project, requires a super user token
        """
        print('Creating project at {}'.format(self.endpoint))
        try:
            api = self._super_api
        except:
            exit('No _super_api for {}. Did you forget to pass a super token?'.format(self.endpoint))
        try:
            res = api.create_project(data=project_csv)
            self.token = str(res.content, 'utf-8')
            self._api = API(self.token, self.endpoint, self.cappy_api_version)
            if is_longitudinal:
                # redcap has a bug when creating longitudinal projects
                # where it creates an empty event with the name 'event_1_arm_1'
                self.run_api_call('delete_events', events=['event_1_arm_1'])
        except:
            exit('Project creation failed for {} with token {}'.format(self.endpoint, self.super_token))

    def run_api_call(self, method, *args, **kwargs):
        call = getattr(self._api, method)
        print('Running {} on endpoint {}'.format(method, self.endpoint))
        return call(*args, **kwargs)

    def _pipe_data(self, source, data_type, **kwargs):
        """
        Pipes the data from one project to the next. Can only be used with api calls that
        dont require super user permissions
        """
        export_method = 'export_' + data_type
        import_method = 'import_' + data_type
        res_ex = source.run_api_call(export_method, **kwargs)
        if data_type == 'records':
            import_method += '_overwrite'
            data = json.loads(str(res.content, 'utf-8'))
            step = 1000
            batches = [data[i : i + step] for i in range(0, len(data), step)]
            for batch in batches:
                kwargs['data'] = json.dumps(batch)
                res_im = self.run_api_call(import_method, **kwargs)
        else:
            kwargs['data'] = res_ex.content
            res_im = self.run_api_call(import_method, **kwargs)

    def copy_project(self, source, initialize=True, pull_metadata=True, pull_data=True):
        """
        When passed an instance of a project, will copy metadata and data
        if their respective flags are turned on.
        """
        if initialize:
            res = source.run_api_call('export_project_info', adhoc_redcap_options={
                'format': 'csv'
            })
            self.create_project(res.content)

        if pull_metadata:
            self._pipe_data(source, 'metadata')
            self._pipe_data(source, 'events')
            self._pipe_data(source, 'arms')
            self._pipe_data(source, 'instrument_event_mapping')

        if pull_data:
            self._pipe_data(source, 'records')


