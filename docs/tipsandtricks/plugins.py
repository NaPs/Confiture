import sys
from pprint import pprint

from confiture import Confiture
from confiture.schema import ValidationError
from confiture.parser import ParsingError
from confiture.schema.containers import Section, Value, many
from confiture.schema.types import Boolean, Integer, String

#
# Our Confiture schemas:
#

class GenericPluginSchema(Section):

    # This value is common to all plugins:
    common_value = Value(Integer())

    # Enable the allow_unknown meta in order to keep unknown values
    # on the first validation:
    _meta = {'allow_unknown': True,
             'repeat': many,
             'args': Value(String())}


class MainConfigurationSchema(Section):

    global_value = Value(Integer())
    plugin = GenericPluginSchema()


#
# Our plugins:
#

class BasePlugin(object):

    name = None
    schema = None

    def __init__(self, config):
        self.config = config

    def print_config(self):
        print '%s: ' % self.__class__.__name__
        pprint(self.config.to_dict())


class BeautifulSchema(GenericPluginSchema):

    beautiful_value = Value(String())

    # The allow_unknown meta is disable to forbid bad config:
    _meta = {'allow_unknown': False}


class BeautifulPlugin(BasePlugin):

    name = 'beautiful'
    schema = BeautifulSchema()


class UglySchema(GenericPluginSchema):

    ugly_value = Value(Boolean())
    _meta = {'allow_unknown': False}


class UglyPlugin(BasePlugin):

    name = 'ugly'
    schema = UglySchema()



#
# Our test config
#

TEST_CONFIG = '''
global_value = 42

plugin 'beautiful' {
    common_value = 123
    beautiful_value = "I'm so beautiful"
}

plugin 'ugly' {
    common_value = 456
    ugly_value = no
}
'''

#
# This is where the magic happen:
#

if __name__ == '__main__':
    my_plugins = (BeautifulPlugin, UglyPlugin)
    enabled_plugins = []

    # Parse the global configuration:
    config = Confiture(TEST_CONFIG, schema=MainConfigurationSchema())
    try:
        pconfig = config.parse()
    except (ValidationError, ParsingError) as err:
        if err.position is not None:
            print str(err.position)
        print err
        sys.exit(1)
    else:
        print 'Main configuration:'
        pprint(pconfig.to_dict())

    # Enable each used plugins:
    for plugin_conf in pconfig.subsections('plugin'):
        # Search the plugin:
        for plugin in my_plugins:
            if plugin.name == plugin_conf.args:
                break
        else:
            print 'Unknown plugin %r, exiting.' % plugin_conf.args
            sys.exit(1)
        # Check plugin configuration:
        try:
            validated_conf = plugin.schema.validate(plugin_conf)
        except ValidationError as err:
            print 'Bad plugin configuration:'
            if err.position is not None:
                print str(err.position)
            print err
            sys.exit(1)
        else:
            # Instanciate the plugin object:
            enabled_plugins.append(plugin(validated_conf))

    # Print each enabled plugin config:
    for plugin in enabled_plugins:
        print '\n' + '~' * 80 + '\n'
        plugin.print_config()

