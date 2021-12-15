from setuptools import setup

setup(
    name='my-github-setup-name',
    version='0.1.0',
    packages=['script'],
    entry_points = {
        'console_scripts': ['my-github=script.main:my_github']
    }
)