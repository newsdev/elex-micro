import os.path
from pip.download import PipSession
from pip.req import parse_requirements

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install_reqs = parse_requirements('requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='elex-micro',
    version='0.0.1',
    author='Jeremy Bowers',
    author_email='jeremy.bowers@nytimes.com',
    url='https://github.com/newsdev/elex-micro',
    description='A diet client for parsing the Associated Press\'s elections API JSON',
    long_description=read('README.md'),
    packages=('elex_micro', 'tests'),
    entry_points={
        'console_scripts': (
            'results = elex_micro.results:main',
            'reportingunits = elex_micro.reportingunits:main',
            'races = elex_micro.races:main',
            'candidates = elex_micro.candidates:main',
        ),
    },
    license="Apache License 2.0",
    keywords='election race candidate democracy news associated press',
    install_requires=reqs,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    )
)
