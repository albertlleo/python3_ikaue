from setuptools import find_packages
import NLP_ikaue

def define_args():
    install_requirements = ['beautifulsoup4>=40.3,<49.2', 'numpy>=1.16,<2.0', 'matplotlib>=3.0.1,<3.2.1', 'xlrd >= 1.0', 'boto3>=1.17.36']

    test_requirements = ['pytest>=4.9.3', 'bs4>=0.0.1','gapic-google-cloud-language-v1>=0.15.3','google-api-core>=1.26.2','google-api-python-client>=2.0.2','urllib3>=1.26.4']
    args = {
        'name': 'NLP_ikaue Python3 IKAUE',
        'version': NLP_ikaue.__version__,
        'url': 'https://github.com/albertlleo/python3_ikaue',
        'author': 'Albert Lleo',
        'author_email': 'albert@ikaue.com',
        'classifiers': ['Development Status :: 3 - Alpha', 'Programming Language :: Python :: 3'],
        'packages':  find_packages(),
        'python_requires': '>=3.5',
        'entry_points': {'console_scripts': ['']},
        'install_requires': install_requirements,
        'extras_require': {'testing': test_requirements},
        'project_urls': {'Source':
                         'https://github.com/albertlleo/python3_ikaue'}
    }
    return args