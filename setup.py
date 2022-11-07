from setuptools import find_packages, setup

setup(
    name='tlapbot',
    version='0.6.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'requests',
        'apscheduler'
    ],
)