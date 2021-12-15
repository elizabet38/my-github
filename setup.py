from setuptools import setup

setup(
    name='my-github-setup-name',
    version='0.1.0',
    packages=['my_github'],
    entry_points = {
        'console_scripts': ['my-github=my_github.main:my_github']
    }
)