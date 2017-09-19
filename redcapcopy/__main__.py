docstr = """
redcapcopy

Usage: rccp [-imdvw] (<config>)

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
    with open(args.get('<config>'), 'r') as config_file:
        config = yaml.load(config_file)

    source = Project(config['source']['endpoint'],
                     config['source']['token'],
                     config['source']['is_super_token'])
    target = Project(config['target']['endpoint'],
                     config['target']['token'],
                     config['target']['is_super_token'])

    if args.get('--write-source-metadata'):
        source.write_metadata(config['source']['metadata_path'])

    target.copy_project(source,
                        verbose=args.get('--verbose'),
                        initialize=args.get('--initialize'),
                        pull_metadata=args.get('--metadata'),
                        metadata_file=config['source']['metadata_path'],
                        pull_data=args.get('--data'))


def cli_run():
    args = docopt(docstr)
    main(args)

if __name__ == '__main__':
    cli_run()
    exit()
