docstr = """
redcapcopy

Usage: rccp [-imdvw] (<config>)
rccp [-itmdvw] (<source_token> <source_endpoint> <target_token> <target_endpoint>) [-m=<path> -t=<title>]

Options:
  -h --help                                     show this message and exit
  -i --initialize                               initialize the target project
  -m=<path>, --metadata=<path>                  copy metadata
  -t=<title>, --title=<title>                   change target project title
  -d --data                                     copy records
  -v --verbose                                  log verbosly
  -w --write-source-metadata                    write metadata from source to file

"""

from docopt import docopt
import yaml

from redcapcopy.project import Project

def main(args):
    if args.get('<config>'):
        with open(args.get('<config>'), 'r') as config_file:
            config = yaml.load(config_file)
    else:
        # for some reason the title in docopt comes through in a list
        config = {
            'source': {
                'token': args.get('<source_token>'),
                'endpoint': args.get('<source_endpoint>'),
                'metadata_path': args.get('--metadata'),
            },
            'target': {
                'token': args.get('<target_token>'),
                'endpoint': args.get('<target_endpoint>'),
                'project_title': args.get('--title')[0],
            }
        }

    source = Project(config['source']['endpoint'],
                     config['source']['token'])
    target = Project(config['target']['endpoint'],
                     config['target']['token'])

    metadata_path = config['source'].get('metadata_path')
    if args.get('--write-source-metadata'):
        if not metadata_path:
            exit("Please provide a metadata_path parameter in the config file to write to")
        else:
            source.write_metadata(metadata_path)

    project_title = config['target'].get('project_title')

    target.copy_project(source,
                        verbose=args.get('--verbose'),
                        initialize=args.get('--initialize'),
                        pull_metadata=args.get('--metadata'),
                        metadata_file=metadata_path,
                        project_title=project_title,
                        pull_data=args.get('--data'),
                        record_copy_options=config.get('record_copy_options'))


def cli_run():
    args = docopt(docstr)
    main(args)

if __name__ == '__main__':
    cli_run()
    exit()
