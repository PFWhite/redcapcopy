
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'My Project',
    'author': 'Patrick White',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'pfwhite@ufl.edu',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['redcapcopy'],
    'entry_points': {
        'console_scripts': [
            'rccp = redcapcopy.__main__:cli_run',
        ],
    },
    'scripts': [],
    'name': 'redcapcopy'
}

setup(**config)

