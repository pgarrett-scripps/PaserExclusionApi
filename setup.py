from setuptools import setup

setup(
    name='exclusionms',
    version='0.0.1',
    description='Pip package to work exclusion list and its components',
    url='https://github.com/pgarrett-scripps/exclusionms',
    author='Patrick Garrett',
    author_email='pgarrett@scripps.edu',
    license='MIT',
    packages=['exclusionms'],
    package_dir={'exclusionms': 'exclusionms'},
    install_requires=['intervaltree==3.1.0',
                      'requests==2.28.1',
                      ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.10',
    ],
)