# coding: utf-8
from setuptools import setup, find_packages

install_requires = [
    'Flask',
    'packaging',
    'PyYAML',
    'cairocffi',
    'pyparsing>=1.5.7',
    'pytz',
    'six',
    'structlog',
    'tzlocal',
]

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='graphite-api',
    version='1.1.3',
    url='https://github.com/brutasse/graphite-api',
    author="Bruno Renié, based on Chris Davis's graphite-web",
    author_email='bruno@renie.fr',
    license='Apache Software License 2.0',
    description=('Graphite-web, without the interface. '
                 'Just the rendering HTTP API.'),
    long_description=long_description,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={
        'sentry': ['raven[flask]'],
        'cyanite': ['cyanite'],
        'cache': ['flask-caching'],
        'statsd': ['statsd'],
    },
    zip_safe=False,
    platforms='any',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: System :: Monitoring',
    ),
    python_requires='>=3.8',
    test_suite='tests',
)
