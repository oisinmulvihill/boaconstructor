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
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


# Force finding lib version first:
sys.path.insert(0, './lib')
import boaconstructor


Name='boaconstructor'
ProjecUrl="http://pypi.python.org/pypi/boaconstructor"
Version=boaconstructor.__version__
Author='Oisin Mulvihill'
AuthorEmail='oisin dot mulvihill a-t gmail d-ot com'
Maintainer=' Oisin Mulvihill'
Summary='The boacontructor is a templating library for *data*, i.e. templating for dictionaries.'
License='Apache License v2.0'
ShortDescription=Summary
Description=r"""The boacontructor is a templating library for *data*.

It allows you to construct Python dictionaries from other templates,
dictionaries or instances.


Source code is available on github:
  * https://github.com/oisinmulvihill/boaconstructor


Documentation is available here:
  * http://packages.python.org/boaconstructor

An Example
----------

I'll let the code and comments do the talking::

    from boaconstructor import Template

    # Some shared information in a dict. This could also be a class instance
    # or something else that supports getattr and hasattr.
    #
    common = dict(
        timeout = 30,
        email = "admin@example.com"
    )

    # This is a template created in a module. You need one of these. I pass in
    # references that are available at this stage. The 'host.$.name' I will pass
    # in at render time.
    #
    webserver_data = Template('webserver',
        dict(
            interface = 'host.$.name',
            port = 32189,
            timeout = 'common.$.timeout',
            alert_email = 'common.$.email',
        ),
        # This is uses common as an 'internal' reference
        references={'common':common}
    )

    # At run time I can pass 'external' references to resolve the hostnames.
    # Maybe I got these from a database or some other source.
    #
    machine_1 = webserver_data.render({'host': {'name': 'myserver1'}}),
    # {'alert_email': 'admin@example.com', 'interface': 'myserver1', 'port': 32189, 'timeout': 30}

    machine_2 = webserver_data.render({'host': {'name': 'myserver2'}}),
    # {'alert_email': 'admin@example.com', 'interface': 'myserver2', 'port': 32189, 'timeout': 30}


    # Now I can pass these to Cheetah/Mako/etc to render a specific type of
    # XML/INI/Text configuration files.




"""

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
