"""
The setup needed to make the package into an egg and release to Pypi.

Oisin Mulvihill
2011-03-26


Copyright 2011 Oisin Mulvihill

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


Name='boaconstructor'
ProjecUrl=""
Version='0.1.0'
Author='Oisin Mulvihill'
AuthorEmail='oisinmulvihill at gmail dot com'
Maintainer=' Oisin Mulvihill'
Summary='Templating for dictionaries.'
License='Apache License v2.0'
ShortDescription=Summary
Description=
    "You have templating for various types of file outputs. This library "
    "offers templating for the *data* passed to other template libraries. "
    "This allows the construction of python dictionaries from other 'template' "
    "dictionaries. "
)

TestSuite = 'boaconstructor.tests'

needed = [
]


EagerResources = [
    'boaconstructor',
]

ProjectScripts = [
]

PackageData = {
    '': ['*.*'],
}

# Make exe versions of the scripts:
EntryPoints = {
}

setup(
#    url=ProjecUrl,
    name=Name,
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=Description,
    license=License,
    scripts=ProjectScripts,
    test_suite=TestSuite,
    install_requires=needed,
    include_package_data=True,
    packages=find_packages('lib'),
    package_data=PackageData,
    package_dir = {'': 'lib'},
    eager_resources = EagerResources,
    entry_points = EntryPoints,
    #namespace_packages = [''],
)
