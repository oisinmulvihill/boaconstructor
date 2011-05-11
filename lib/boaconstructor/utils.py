"""
.. module::`utils`
    :platform: Unix, Windows
    :synopsis: Provides the functions that boaconstructor Template relies on.


Exceptions
++++++++++

.. autoclass:: ReferenceError

.. autoclass:: AttributeError

.. autoclass:: DeriveFromError

.. autoclass:: MultipleDeriveFromError

render
++++++

.. autofunction:: render

parse_value
+++++++++++

.. autofunction:: parse_value

resolve_references
++++++++++++++++++

.. autofunction:: resolve_references

build_ref_cache
+++++++++++++++

.. autofunction:: build_ref_cache

RenderState
+++++++++++

.. autoclass:: RenderState

hunt_n_resolve
++++++++++++++

.. autofunction:: hunt_n_resolve


what_is_required
++++++++++++++++

.. autofunction:: what_is_required


has
+++

.. autofunction:: has

get
+++

.. autofunction:: get

"""
__all__ = [
    'parse_value', 'ReferenceError', 'AttributeError', 'has', 'get',
    'resolve_references', 'build_ref_cache', 'hunt_n_resolve', 'render',
    'what_is_required', 'RenderState', "DeriveFromError",
    "MultipleDeriveFromError",
]

import re
import types
import pprint


# Reference-Attribute recovery <reference>.$.<attribute>
REFATT_RE = re.compile(r"(?P<ref>.*)(?P<refatt>\.\$\.)(?P<attr>.*)")

# All-Inclusion recovery <allfrom>.*
ALLINC_RE = re.compile(r"^(?P<allfrom>.*)(?P<all>\.\*)$")

# Derive from recovery dervicefrom.[<reference>]
DERIVEFROM_RE =  re.compile(r"^derivefrom\.\[(?P<derivefrom>.*)\]$")


class ReferenceError(Exception):
    """Raised when a reference name could not found in references given.

    """
    def __init__(self, msg, ref, *args):
        self.message = msg
        self.reference = ref
        self.args = [msg,]


class AttributeError(Exception):
    """Raised when an attribute was not found for the references given.

    """
    def __init__(self, msg, attr, *args):
        self.message = msg
        self.attribute = attr
        self.args = [msg,]


class DeriveFromError(Exception):
    """Raised for problems with derivefrom.[<value>] recovered item for the value.
    """
    def __init__(self, msg, found, *args):
        self.message = msg
        self.found = found
        self.args = [msg,]


class MultipleDeriveFromError(Exception):
    """Raised while attempting to have multiple derivefroms in the same template.
    """


def parse_value(value):
    """Recover the ref-attr, all-inclusion or derive from if present.

    :returns: The results of parsing the given value string.

    This is a dict in the form:

    .. code-block:: python

        dict(
            found='refatt', 'all', 'derivefrom' or None,
            reference='' or '<reference string recovered>',
            attribute='' or '<attribute string recovered>',
            allfrom='' or '<all inclusion string recovered>',
            derivefrom='' or 'derivefrom string recovered',
        )

    """
    returned = dict(found=None,reference='',attribute='',allfrom='')

    if type(value) in types.StringTypes:
        # Only bother with strings, ignore everything else.
        #print "value to parse: '%s'." % value
        if value.strip() == '.*':
            # ignore empty .* inclusion
            return returned

        refatt_result = re.search(REFATT_RE, value)
        allinc_result = re.search(ALLINC_RE, value)
        derivefrom_result = re.search(DERIVEFROM_RE, value)

        if refatt_result:
            found = refatt_result.groupdict()
            #print "found: '%s'" % pprint.pformat(found))
            #print "groups", refatt_result.groups())

            returned['found'] = 'refatt'
            returned['reference'] = found.get('ref')
            returned['attribute'] = found.get('attr')

        if allinc_result:
            found = allinc_result.groupdict()
            #print("found: '%s'" % pprint.pformat(found))
            #print("groups", allinc_result.groups())

            returned['found'] = 'all'
            returned['allfrom'] = found.get('allfrom')

        if derivefrom_result:
            found = derivefrom_result.groupdict()
            #print("found: '%s'" % pprint.pformat(found))
            #print("groups", derivefrom_result.groups())

            returned['found'] = 'derivefrom'
            returned['derivefrom'] = found.get('derivefrom')

    return returned


def has(reference, attribute):
    """Check if the dict, instance or Template instance has a given attribute.

    :param reference: A dict, Template instance or a object instance.

    :param attribute: A string representing the key/member variable to recover.

    :returns: True yes, False no.

    """
    returned = False

    if type(reference) in (types.DictType, types.DictProxyType):
        returned = attribute in reference

    elif hasattr(reference, 'content'):
        # core.Template like: Look inside the content and not the
        # Template object itself.
        returned = attribute in getattr(reference, 'content')

    else:
        # Assume it is an instance of some kind which supports hasattr:
        returned = hasattr(reference, attribute)

    return returned


def get(reference, attribute):
    """Get the attribute value from the given dict, object instance or Template instance.

    :param reference: A dict, Template instance or a object instance.

    :param attribute: A string representing the key/member variable to recover.

    :returns: The value found. If nothing could be recovered then AttributeError will be raised.

    """
    found = False
    returned = False

    if type(reference) in (types.DictType, types.DictProxyType):
        if attribute in reference:
            found = True
            returned = reference[attribute]


    elif hasattr(reference, 'content'):
        # core.Template like: Look inside the content and not the
        # Template object itself.
        r = getattr(reference, 'content')
        if attribute in r:
            found = True
            returned = r[attribute]

    else:
        # Assume it is an instance of some kind which supports getattr:
        if hasattr(reference, attribute):
            found = True
            returned = getattr(reference, attribute)

    if not found:
        raise AttributeError("The attribute '%s' in any reference!" % (
                attribute
            ),
            attr=attribute
        )

    return returned


def resolve_references(reference, attribute, int_references, ext_references={}):
    """Work out the attribute value for a reference from the internal or external references.

    This is usually call by the Template.resolve method.

    :param reference: This is the <reference> string recovered from a call to parse_value.

    :param attribute: This is the dict key we must look up in the references.

    This is the <attribute> recovered from a call to parse_value. If this is
    None then only the reference will be resolved. What it points at will then
    be returned.

    :param int_references: This the reference dict usually representing the reference stored as a member of the Template class.

    :param ext_references: This the reference dict usually representing the reference given as an argument to render.

    The ext_references is given priority over the int_references.

    If a reference-attribute is found, then int_references will not be consulted.

    If the reference is not found in int_references or ext_references then
    ReferenceError will be raised.

    If the attribute is not found in in the any of the reference dicts, then
    AttributeError will be raised.

    :returns: The value or item pointed at by the reference and / or attribute.

    """
    found = False
    returned = ""

    ref_present = reference in ext_references or reference in int_references
    if not ref_present:
        # The reference is not present at all, abandon.
        raise ReferenceError("The reference '%s' could not be resolved!" % (
                reference
            ),
            reference
        )

    # Look for the attribute in the ext_references:
    ext_result = None
    if has(ext_references, reference):
        r = get(ext_references, reference)

        if not attribute:
            # all-inclusion operation, return the reference
            found = True
            returned = r

        elif has(r, attribute):
            # Success, skip int_references lookup:
            found = True
            returned = get(r, attribute)

    int_result = None
    if not found and has(int_references, reference):
        # Nothing was found in externals so try in the internal references.
        r = get(int_references, reference)

        if not attribute:
            # all-inclusion operation, return the reference
            found = True
            returned = r

        elif has(r, attribute):
            found = True
            # Hurragh, its here.
            returned = get(r, attribute)

    if not found:
        raise AttributeError("Attribute '%s' was not be found in '%s' or any other references!" % (
                attribute,
                reference
            ),
            attribute
        )

    return returned


def build_ref_cache(int_refs, ext_refs):
    """Work out all the references and child references from the internal and
    externally given references.

    This in effect flattens the references and making lookup faster for
    hunt_n_resolve.

    :param int_refs: a dict of 'dicts and/or Template' instances.

    :param ext_refs: a dict of 'dicts and/or Template' instances.

    :returns: a dict with the results in the form:

    .. code-block:: python

        results = {
            'int':{ ... },
            'ext':{ ... }
        }

    For an example of this see tests/testboacontructor.py:DataTemplate and
    'testBuildRefCache()'.

    """
    reference_cache = {'int':{}, 'ext':{}}

    def recover(items, dest):
        # Store the references:
        for reference, source in items:
            reference_cache[dest][reference] = source
            # Unpack and store the 'child' references if any are present:
            if hasattr(source, 'references'):
                children = getattr(source,'references').items()
                recover(children, dest)

    recover(int_refs.items(), dest='int')
    recover(ext_refs.items(), dest='ext')

    return reference_cache


class RenderState(object):
    """This is used to track what is going on where in the render process.
    """
    def __init__(self, template, int_refs={}, ext_refs={}, name='', parent=None, reference_cache=None):
        """
        :param template: This is the data template used for this state's render process.

        :param int_refs: A dict of internal references.

        :param ext_refs: A dict of external references.

        :param name: A string name or user identifier for this state.

        :param parent: This is None usually unless, through render recursion, this is a sub state.

        :param reference_cache: None unless its a sub state using the parents cache.

        The reference cache is created from the given int_refs  and ext_refs.

        """
        self.parent = parent
        self.name= name
        self._template = template
        self._substates = []
        self._deriveFrom = dict(name='', data={})

        # Work out all the references, in effect flattening the references and
        # making lookup faster later on.
        if not reference_cache:
            self.referenceCache = build_ref_cache(int_refs, ext_refs)
        else:
            self.referenceCache = reference_cache


    def subState(self, item, name):
        """Return a new state for a child template render."""
        state = RenderState(
            item,
            parent=self,
            reference_cache=self.referenceCache,
            name=name,
        )

        # Record the substates created while render this parent template
        self._substates.append((name, state))

        return state


    def hasDeriveFrom(self):
        """Check if this template has data to derivefrom."""
        return self._deriveFrom['data'] != {}


    def setDeriveFrom(self, name, data):
        """Only a single derivefrom is supported, not multiple.

        DeriveFromError will be raise if this has been set previously.

        """
        if self.hasDeriveFrom():
            raise MultipleDeriveFromError((
                    "The template '%s' has a derivefrom set previously '%s'. "
                    "More then one is not supported."
                ) % (
                self.name,
                self._deriveFrom['name']
            ))

        self._deriveFrom['name'] = name
        self._deriveFrom['data'] = data
        #print("setDeriveFrom: <%s> " % pprint.pformat(self._deriveFrom))


    def getDeriveFrom(self):
        return self._deriveFrom['data']


    def getDataTemplate(self):
        return self._template

    template = property(getDataTemplate)


    def resolveReferences(self, reference, attribute):
        """This wraps resolve_references providing the interal and external ref dicts.
        """
        # TODO: I can catch exceptions here to provide a traceback of
        # where we are before raising the exceptions again.

        rc = resolve_references(
            reference,
            attribute,
            self.referenceCache['int'],
            self.referenceCache['ext'],
        )

        return rc


def hunt_n_resolve(value, state):
    """Resolve a single attribute using the given reference_cache.

    :param value:
    :param state: An instance of RenderState contain

    :returns: The value the attribute points at.

    If the value is not an attribute it is passed through unprocessed.

    """
    # Hunt for the last non reference-attribute i.e the actual value
    returned = value

    while True:
        result = parse_value(returned)

        if result['found'] == 'refatt':
            # Resolve what this reference points at. Then loop to
            # check if this is also really a reference. Progress in
            # this way until no more ref-attrs are found. I.e. we've
            # got the actual value at the end of the pointer rainbow.
            #
            returned, attribute = result['reference'], result['attribute']
            if returned:
                returned = state.resolveReferences(returned, attribute)


        elif result['found'] == 'all':
            # Recover the dict to add and then loop over it in turn
            # resolving any references.
            #
            #print("** ALL: get all content for **\n%s\n" % result['allfrom'])
            allfrom = result['allfrom']
            found = state.resolveReferences(allfrom, None)

            if hasattr(found, 'items'):
                # Now recurse to create the output dict this attribute
                # should contain.
                returned = render(state.subState(found, name=allfrom))

            else:
                # This doesn't appear to be dict-like return the original
                # value. This could be a string, number, etc.
                returned = found


        elif result['found'] == 'derivefrom':
            derivefrom = result['derivefrom']

            found = state.resolveReferences(derivefrom, None)

            # This must be a dict-like item.
            if hasattr(found, 'items'):
                # Now recurse to create the dict we will use to derivefrom.
                returned = render(state.subState(found, name=derivefrom))
                state.setDeriveFrom(derivefrom, returned)

            else:
                msg = "The derivefrom '%s' does not appear to resolve to a template or dict like object!" % derivefrom
                raise DeriveFromError(msg,found)

            returned = '' # prevent looping forever.

        else:
            the_type = type(value)

            # Is this an iterable? If so we need to check each entry to
            # see if its a ref-attr, all-inc, etc
            if hasattr(value, '__iter__') and not hasattr(value, 'items'):
                # ignore dicts, this would iterate over the keys which
                # is not what we want.
                #
                # We need to check across the contents of the iterable
                # and resolve ref-attr or all-inc entries found.
                returned = []
                for item in value:
                    returned.append(hunt_n_resolve(item, state))

            elif hasattr(value, 'items'):
                # We need to render this dict like item:
                #print "0. Here: <%s>" % pprint.pformat(value)
                returned = render(state.subState(value, name='sub-dict'))

            # Ok, exit.
            break

    return returned


def what_is_required(template):
    """Recover the 'top-level' references the given template requires.

    :para template: This is a dict / templatewhich provides the items() method.

    This should returning a list of (key, value) pairs.

    Aliases are not resolved. This is purley the references mentioned in the
    dict structure.

    This does not scan internal / external references the template may provides.
    It only goes through the dict values checking for ref-attr or allinc. If the
    value found is a list, it will recurse look through it too.

    :returns: This is a dict whose keys are the references found.

    For example:

    .. code-block:: python

        >>> from boaconstructor import Template
        >>> from boaconstructor.utils import what_is_required
        >>>
        >>> test2 = Template(
        ...     'test2',
        ...     dict(
        ...         x='derivefrom.[trucks]',
        ...         items=[
        ...             dict(abc='derivefrom.[cars]'),
        ...         ],
        ...         host='test1.*',
        ...         stuff=[
        ...             'com.$.keep',
        ...             ["frank.*",]
        ...         ]
        ...     ),
        ... )
        >>>
        >>> result = what_is_required(test2)
        >>>
        >>> print result
        {'test1': 1, 'cars': 1, 'com': 1, 'trucks': 1, 'frank': 1}

    """
    required = {}

    def list_recurse(items):
        for item in items:
            result = parse_value(item)
            if result['found'] == 'refatt':
                required[result['reference']] = 1

            elif result['found'] == 'all':
                required[result['allfrom']] = 1

            elif result['found'] == 'derivefrom':
                required[result['derivefrom']] = 1

            else:
                if hasattr(item, '__iter__') and not hasattr(item, 'items'):
                    list_recurse(item)

                elif hasattr(item, 'items'):
                    # We need to render this dict like item:
                    #print "A. Here: <%s>" % pprint.pformat(item)
                    list_recurse(item.items())

    for top_level_ref, attr_or_ref in template.items():
        result = parse_value(attr_or_ref)

        if result['found'] == 'refatt':
            required[result['reference']] = 1

        elif result['found'] == 'all':
            required[result['allfrom']] = 1

        elif result['found'] == 'derivefrom':
            required[result['derivefrom']] = 1

        else:
            the_type = type(attr_or_ref)

            # Is this an iterable? If so we need to check each entry to
            # see if its a ref-attr or all-inc.
            if hasattr(attr_or_ref, '__iter__') and not hasattr(attr_or_ref, 'items'):
                list_recurse(attr_or_ref)

            elif hasattr(attr_or_ref, 'items'):
                # We need to render this dict like item:
                #print "B. Here: <%s>" % pprint.pformat(attr_or_ref)
                list_recurse(attr_or_ref.items())

    return required


def render(state):
    """Construct the final dictionary after resolving all references to get their actual values.

    :param state: The is an instance of RenderState set up ready from the render process to begin.

    :returns: A single dict representing the combination of all parts after references have been resolved.

    """
    returned = {}
    derivefrom = {}

    for key, attr_or_ref in state.template.items():
        rc = hunt_n_resolve(attr_or_ref, state)

        # only check for derivefrom when its not {} if its present in state:
        if state.hasDeriveFrom() and not derivefrom:
            # We have a dict to derive from. This means the key, attr_or_ref
            # need to be removed in the final output.
            #print("has derive from. Removing from output: <%s:%s> " % (key, attr_or_ref))
            derivefrom = state.getDeriveFrom()

        else:
            # Replace the value as normal.
            returned[key] = rc

    if derivefrom:
        # Overwrite the rendered derivefrom with values from the main template
        # (if there are any shared keys). The derivefrom is a fully resolved
        # dict at this point
        #
        derivefrom.update(returned)
        returned = derivefrom

    return returned
