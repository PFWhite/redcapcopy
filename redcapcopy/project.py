import json
from types import SimpleNamespace

from cappy import API

from redcapcopy.util import is_super_token

class Project(object):

    def __init__(self, endpoint, token):
        self.cappy_super_version = 'v6.16.0.redi_ready.json'
        self.cappy_api_version = 'master.yaml'
        self.endpoint = endpoint
        if is_super_token(token):
            self._super_api = API(token, endpoint, self.cappy_super_version)
            self.super_token = token
        else:
            self._api = API(token, endpoint, self.cappy_api_version)
            self.token = token

    def create_project(self, project_csv, verbose, is_longitudinal=True):
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
            if verbose:
                print(res.status_code, (res.content if str(res.status_code) != '200' else ''))
            self.token = str(res.content, 'utf-8')
            self._api = API(self.token, self.endpoint, self.cappy_api_version)
            if is_longitudinal:
                # redcap has a bug when creating longitudinal projects
                # where it creates an empty event with the name 'event_1_arm_1'
                self.run_api_call('delete_events', events=['event_1_arm_1'])
                if verbose:
                    print(res.status_code, (res.content if str(res.status_code) != '200' else ''))
        except Exception as ex:
            raise ex
            exit('Project creation failed for {} with token {}'.format(self.endpoint, self.super_token))

    def run_api_call(self, method, *args, **kwargs):
        call = getattr(self._api, method)
        print('Running {} on endpoint {}'.format(method, self.endpoint))
        return call(*args, **kwargs)

    def _batch_records(self, import_method, raw_data, verbose=False, batch_size=1000, **kwargs):
        import_method += '_overwrite'
        data = json.loads(str(raw_data, 'utf-8'))
        batches = [data[i : i + batch_size] for i in range(0, len(data), )]
        for batch in batches:
            kwargs['data'] = json.dumps(batch)
            res_im = self.run_api_call(import_method, **kwargs)
            if verbose:
                print('status code: ' + str(res_im.status_code),
                        '\n' + (str(res_im.content, 'utf-8') if str(res_im.status_code) != '200' else ''))

    def _get_raw_data(self, source, export_method, **kwargs):
        """
        Returns the export response or a mock with local file system data
        """
        if kwargs.get('data_file'):
            print('Using data file at {data_file} for {export_method}'.format(export_method=export_method, **kwargs))
            file_path = kwargs.get('data_file')
            with open(file_path, 'rb') as data_file:
                res_ex = SimpleNamespace()
                res_ex.status_code = 200
                res_ex.content = data_file.read()
            del kwargs['data_file']
        else:
            res_ex = source.run_api_call(export_method, **kwargs)
            raw_data = res_ex.content
        return res_ex


    def _pipe_data(self, source, data_type, verbose, **kwargs):
        """
        Pipes the data from one project to the next. Can only be used with api calls that
        dont require super user permissions

        Can be used with a data file instead of calling from a server
        """
        export_method = 'export_' + data_type
        import_method = 'import_' + data_type
        res_ex = self._get_raw_data(source, export_method, **kwargs)
        if verbose and not kwargs.get('data_file'):
            print(res_ex.status_code, (res_ex.content if str(res_ex.status_code) != '200' else ''))
        if data_type == 'records':
            self._batch_records(import_method, res_ex.content, verbose, **kwargs)
        else:
            kwargs['data'] = res_ex.content
            res_im = self.run_api_call(import_method, **kwargs)
            if verbose:
                print(res_im.status_code, (res_im.content if str(res_im.status_code) != '200' else ''))

    def copy_project(self, source,
                     verbose=False,
                     initialize=True,
                     pull_metadata=True,
                     metadata_file=None,
                     pull_data=True,
                     record_copy_options={}):
        """
        When passed an instance of a project, will copy metadata and data
        if their respective flags are turned on.
        """
        if initialize:
            res = source.run_api_call('export_project_info', adhoc_redcap_options={
                'format': 'csv'
            })
            self.create_project(res.content, verbose)

        if pull_metadata:
            # the order of these is super important. Dont change
            self._pipe_data(source, 'metadata', verbose, data_file=metadata_file)
            self._pipe_data(source, 'arms', verbose)
            self._pipe_data(source, 'events', verbose)
            self._pipe_data(source, 'instrument_event_mapping', verbose)

        if pull_data:
            self._pipe_data(source, 'records', verbose, **record_copy_options)

        if not (initialize or pull_metadata or pull_data):
            exit('Nothing was copied. Make sure to specify with command flags what you want to copy.')

    def write_metadata(self, path):
        with open(path, 'wb') as mfile:
            res = self.run_api_call('export_metadata')
            mfile.write(res.content)
