"""

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
import types

import utils

class TemplateError(Exception):
    """Raised for problems render or otherwise processing templates."""


class Template(object):
    """
    Template represents a dict which may or may not refer to data from
    other dicts.

    Example:

        # Data to be used in host1 and host2
        common = Template('common', {
            "timeout": 42
        })

        # Uses data from common:
        host1 = Template('host1', {
                "host": "1.2.3.4",
                "flag": False,
                "timeout": 'common.$.timeout'
            },
            references = {'common':common}
        )

        # Uses data from common and host1
        host2 = Template('host2', {
                "host": "4.3.2.1",
                "flag": 'host.$.flag',
                "timeout": 'common.$.timeout',
            },
        )

        # Render the 'host1' dict:
        >> host1.render()
        {"host":"1.2.3.4","flag":True,"timeout":42}

        # Render the 'host2' dict:
        >> host2.render(
            references = {
                'common': common,
                'host': host1,
            }
        )
        {"host":"1.2.3.4","flag":True,"timeout":42}

    Notes:
      * A template refence is a dictionary value string containing ".$.". It
        has the format:

            "<template reference>.$.<attribute from template's content>".

      * The references can be given to the constructor or at render
        time. If both are given the render version is used.

      * In host2.render(...) above the reference 'host' was
        used as an alias to 'host1'.

    """
    def __init__(self, name, content, references={}):
        """
        :param name: the string name used to identify this template
        if references.

        :param content: this must be a dict or TemplateError
        will be raised.

        :param references: this is a dict of string to template
        mappings. This is used to resolve references to other
        templates.

        """
        self.name = name
        if type(content) != types.DictType:
            raise TemplateError("The content given is not a Dict!")
        self.content = content
        self.references = references


    def render(self, references={}):
        """Generate a data dict from this template and any it references.

        :param references: this is a dict of string to template
        mappings. This is used to resolve references to other
        templates. If this is empty self.references will be used
        instead.

        :returns: This returns a 'rendered' dict.

        """
        return utils.render(
            self.content.items(),
            int_refs=self.references,
            ext_refs=references,
        )


    def __str__(self):
        return str(self.content)


    def __repr__(self):
        return "'Template <%s>: %s'" % (self.name, self.content)
