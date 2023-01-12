from setuptools import find_packages, setup

setup(
    name='tlapbot',
    version='1.1.0a2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'requests',
        'apscheduler'
    ],
)