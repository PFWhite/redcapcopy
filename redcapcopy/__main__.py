docstr = """
redcapcopy

Usage: rccp [-imdvw] (<config>)
rccp [-imdvw] (<source_token> <source_endpoint> <target_token> <target_endpoint>) [-m <metadata_path>]

Options:
  -h --help                                     show this message and exit
  -i --initialize                               initialize the target project
  -m --metadata                                 copy metadata
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
        config = {
            'source': {
                'token': args.get('<source_token>'),
                'endpoint': args.get('<source_endpoint>'),
                'metadata_path': args.get('<metadata_path>'),
            },
            'target': {
                'token': args.get('<target_token>'),
                'endpoint': args.get('<target_endpoint>'),
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

    target.copy_project(source,
                        verbose=args.get('--verbose'),
                        initialize=args.get('--initialize'),
                        pull_metadata=args.get('--metadata'),
                        metadata_file=metadata_path,
                        pull_data=args.get('--data'),
                        record_copy_options=config.get('record_copy_options'))


def cli_run():
    args = docopt(docstr)
    main(args)

if __name__ == '__main__':
    cli_run()
    exit()
