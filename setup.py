#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ["esm_tools @ git+https://github.com/esm-tools/esm_tools.git",
                "esm_parser @ git+https://github.com/esm-tools/esm_parser.git",
                "esm_runscripts @ git+https://github.com/esm-tools/esm_runscripts.git",
                "colorama",
                "coloredlogs",
                "questionary",
                "regex",
                "loguru",
               ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Miguel Andres-Martinez",
    author_email='miguel.andres-martinez@awi,de',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="ESM automatic testing for ESM-Tools",
    entry_points={
        'console_scripts': [
            'esm_tests=esm_tests.cli:main',
        ],
    },
    install_requires=requirements,
    license="GNU General Public License v2",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='esm_tests',
    name='esm_tests',
    packages=find_packages(include=['esm_tests', 'esm_tests.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/esm-tools/esm_tests',
    version="5.1.0",
    zip_safe=False,
)
