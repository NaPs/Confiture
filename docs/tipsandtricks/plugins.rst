Validate plugins configuration
==============================

If your application use a plugin system, and you want to validate a
configuration which can be different for each plugin, this trick is for you.


The idea is pretty simple, do a two-step validation: the first one will
validate all the common configuration, and the second step validate
each plugin's configuration. To avoid ValidationError in the first step, you
use the ``allow_unknown`` feature of Sections.

Here is a full example:

.. literalinclude:: plugins.py

And the output::

    Main configuration:
    {'global_value': 42,
     'plugin': [{'beautiful_value': "I'm so beautiful", 'common_value': 123},
                {'common_value': 456, 'ugly_value': False}]}

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    BeautifulPlugin: 
    {'beautiful_value': "I'm so beautiful", 'common_value': 123}

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    UglyPlugin: 
    {'common_value': 456, 'ugly_value': False}

