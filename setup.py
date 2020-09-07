#!/usr/bin/env python3

from setuptools import setup


setup(
    name='fuo_dl',
    version='0.1',
    description='feeluown download plugin',
    author='Cosven',
    author_email='yinshaowen241@gmail.com',
    packages=[
        'fuo_dl',
    ],
    package_data={
        '': []
        },
    url='https://github.com/feeluown/feeluown-download',
    keywords=['feeluown', 'plugin', 'download'],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        ),
    install_requires=['feeluown>=3.5.3', 'requests'],
    entry_points={
        'fuo.plugins_v1': [
            'download = fuo_dl',
        ]
    },
)
