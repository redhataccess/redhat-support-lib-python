from setuptools import setup, find_packages


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
    packages=find_packages("src"),
    py_modules=['redhat_support_lib.api'],
    install_requires=['lxml > 2.0',
                      'rpm-python',
                      'python-dateutil'],
    **version_info
)
