from distutils.command.build import build
from setuptools import setup, Command
import os
import sys


version_info = {
    'name': 'redhat-support-lib-python',
    'version': '1.2.3',
    'description': 'Red Hat Support Software Development Library',
    'author': 'Keith Robertson',
    'author_email': 'kroberts@redhat.com',
    'url': 'https://api.access.redhat.com',
    'license': 'ASL2',
    'classifiers': [
        'Development Status :: 1',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ASL2 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.4'],
}


setup(
    package_dir={'': 'src'},
    packages=['redhat_support_lib.infrastructure',
              'redhat_support_lib.utils',
              'redhat_support_lib.web',
              'redhat_support_lib.xml'],
    py_modules=['redhat_support_lib.api'],
    install_requires=['lxml > 2.0',
                      'rpm-python',
                      'python-dateutil'],
    **version_info
)
