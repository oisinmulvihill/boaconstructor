"""
.. module::`utils`
    :platform: Unix, Windows
    :synopsis: Provides the functions that boaconstructor Template relies on.


Exceptions
++++++++++

.. autoclass:: ReferenceError

.. autoclass:: AttributeError

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

hunt_n_resolve
++++++++++++++

.. autofunction:: hunt_n_resolve

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
]

import re
import types
import pprint


# Reference-Attribute recovery <reference>.$.<attribute>
REFATT_RE = re.compile(r"(?P<ref>.*)(?P<refatt>\.\$\.)(?P<attr>.*)")

# All-Inclusion recovery <allfrom>.*
ALLINC_RE = re.compile(r"^(?P<allfrom>.*)(?P<all>\.\*)$")


def parse_value(value):
    """Recover the ref-attr or the all-inclusion if present.

    :returns: The results of parsing the given value string.

    This is a dict in the form:

    .. code-block:: python

        dict(
            found='refatt' or 'all' or None
            reference='' or '<reference string recovered>'
            attribute='' or '<attribute string recovered>'
            allfrom='' or '<all inclusion string recovered>'
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

    return returned


class ReferenceError(Exception):
    """Raised when a reference name could not found in references given."""


class AttributeError(Exception):
    """Raised when an attribute was not found for the references given."""


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
        raise AttributeError("The attribute '%s' in any reference!" % attribute)

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

    #print("\n\nreference '%s' attribute '%s'\nint_references: '%s'\next_references: '%s'\n\n" % (reference, attribute, int_references, ext_references))

    ref_present = reference in ext_references or reference in int_references
    if not ref_present:
        # The reference is not present at all, abandon.
        raise ReferenceError("The reference '%s' could not be resolved!" % reference)

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
        raise AttributeError("The attribute '%s' in any reference!" % attribute)

    return returned


def build_ref_cache(int_refs, ext_refs):
    """Work out all the references and child references from the internal and
    externally given references.

    This in effect flattens the references and making lookup faster for
    recursive_render.

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


def hunt_n_resolve(value, reference_cache):
    """Resolve a single attribute using the given reference_cache.

    :returns: The value the attribute points at.

    If the value is not an attribute it is passed through unprocessed.

    """
    # Hunt for the last non reference-attribute i.e the actual value
    loop_count = 0
    returned = value

    # Prevent looping forever on problems:
    retries = 20
    while retries:
        retries -= 1

        #print("loop_count '%s', value: '%s'" %(loop_count, value))

        result = parse_value(returned)

        if result['found'] == 'refatt':
            # Resolve what this reference points at. Then loop to
            # check if this is also really a reference. Progress in
            # this way until no more ref-attrs are found. I.e. we've
            # got the actual value at the end of the pointer rainbow.
            #
            returned, attribute = result['reference'], result['attribute']

            if returned:
                returned = resolve_references(
                        returned,
                        attribute,
                        reference_cache['int'],
                        reference_cache['ext'],
                )

        elif result['found'] == 'all':
            # Recover the dict to add and then loop over it in turn
            # resolving any references.
            #
            #print("** ALL: get all content for **\n%s\n" % result['allfrom'])

            returned = resolve_references(
                result['allfrom'],
                None,
                reference_cache['int'],
                reference_cache['ext'],
            )

            # Now recurse to create the output dict this attribute should contain.
            returned = render(
                returned.items(),
                # No need to regenerate this, use our one.
                reference_cache=reference_cache,
            )


        else:
            # Is this an iterable? If so we need to check each entry to
            # see if its a ref-attr or all-inc.
            if hasattr(value, '__iter__') and type(value) != types.DictType:
                # ignore dicts, this would iterate over the keys which
                # is not what we want.
                #
                # We need to check across the contents of the iterable
                # and resolve ref-attr or all-inc entries found.
                returned = []
                for item in value:
                    returned.append(hunt_n_resolve(item, reference_cache))

            # Ok, exit.
            break

        loop_count += 1

    return returned


def render(top_level_items, int_refs=None, ext_refs=None, reference_cache=None, extendwith=None):
    """Construct the final dictionary after resolving all references to get their actual values.

    :param top_level_items: A list of key, value items to use.

    The value will be checked to see if it needs resolving. If so, the content
    it points at will be worked out and assigned.

    :param int_refs: A dict of internal references.

    This can only be None if a pre-calculated reference_cache has been given.

    :param ext_refs: A dict of external references.

    This can only be None if a pre-calculated reference_cache has been given.

    :param reference_cache: This is the result of a call to :py:func:`build_ref_cache`.

    :param extendwith: This is a template to render and add to the one we've just rendered template.

    This will use the rendered dict's update(). The main template we are render
    will overwrite any common keys. This is used for a generic template and
    specific templates.

    :returns: A single dict representing the combination of all parts after references have been resolved.

    """
    returned = {}
    loop_count = 0

    # Work out all the references, in effect flattening the
    # references and making lookup faster later on.
    if not reference_cache:
        reference_cache = build_ref_cache(int_refs, ext_refs)

    #print("\n\nreference_cache:\n%s\n\n" % pprint.pformat(reference_cache))

    for top_level_ref, attr_or_ref in top_level_items:
        returned[top_level_ref] = hunt_n_resolve(attr_or_ref, reference_cache)

    if extendwith:
        # Extend the returned dict with the content from extendwith, after it
        # goes through the resolve process.
        pending = {}
        for ref, attr_or_ref in extendwith.items():
            pending[ref] = hunt_n_resolve(attr_or_ref, reference_cache)

        # Overwrite the rendered extendwith with values from the main template
        # (if there are any shared keys).
        pending.update(returned)
        returned = pending

    return returned
