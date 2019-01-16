#!/usr/bin/env python3

from setuptools import setup


setup(
    name='fuo_dl',
    version='0.1.dev0',
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
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        ),
    install_requires=[],
    entry_points={
        'fuo.plugins_v2': [
            'download = fuo_dl',
        ]
    },
)
