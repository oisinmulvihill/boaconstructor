"""
.. module::`core`
    :platform: Unix, Windows
    :synopsis: Provides the high level Template class.

.. autoclass:: TemplateError

.. autoclass:: Template

"""
__all__ = ['TemplateError', 'Template']

import types

from boaconstructor import utils




class TemplateError(Exception):
    """Raised for problems render or otherwise processing templates."""


class Template(object):
    """Template represents a dict which may or may not refer to data from
    other dicts.

    Example:

    .. code-block:: python

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
        has the format::

        "<template reference>.$.<attribute from template's content>".

      * The references can be given to the constructor or at render time. If
        both are given the render version is used.

      * In host2.render(...) above the reference 'host' was used as an alias to
        'host1'.

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


    def render(self, references={}, extendwith={}):
        """Generate a data dict from this template and any it references.

        :param references: this is a dict of string to template mappings.

        This is used to resolve references to other templates. If this is empty
        self.references will be used instead.


        :param extendwith: This is the template to render and then add to this one.

        This will use the rendered dict's update(). This template will overwrite
        any common keys in the rendered extendwith.


        :returns: This returns a 'rendered' dict.

        All references  will have been replaced with the value the point at.

        """
        return utils.render(
            self.content.items(),
            int_refs=self.references,
            ext_refs=references,
            extendwith=extendwith,
        )


    def items(self):
        """Used in an all-inclusion render to return our contained content dict.
        """
        return self.content.items()


    def __str__(self):
        """Show a string version of the content dict we hold.
        """
        return str(self.content)


    def __repr__(self):
        """Show the template name and content we hold.
        """
        return "'Template <%s>: %s'" % (self.name, self.content)
