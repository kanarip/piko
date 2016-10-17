# -*- coding: utf-8 -*-
# Copyright 2010-2015 Kolab Systems AG (http://www.kolabsys.com)
#
# Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen a kolabsys.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os

from optparse import OptionGroup
from optparse import OptionParser
from ConfigParser import SafeConfigParser

import piko

from piko.translate import _

log = piko.getLogger('piko.conf')

class Defaults(object):

    def __init__(self):
        pass

class Conf(object):
    cli_parser = None
    cli_args = None
    cli_keywords = None
    defaults = Defaults()

    def __init__(self):
        # Enterprise Linux 5 does not have an "epilog" parameter to OptionParser
        try:
            self.cli_parser = OptionParser(epilog=epilog)
        except:
            self.cli_parser = OptionParser()

        ##
        ## Runtime Options
        ##
        runtime_group = OptionGroup(self.cli_parser, _("Runtime Options"))
        runtime_group.add_option(
                "-c", "--config",
                dest    = "config_file",
                action  = "store",
                default = os.path.expanduser("~/.pikorc"),
                help    = _("Configuration file to use")
            )

        runtime_group.add_option(
                "-d", "--debug",
                dest    = "debuglevel",
                type    = 'int',
                default = 0,
                help    = _("Set the debugging " + \
                            "verbosity. Maximum is 9, tracing " + \
                            "protocols like LDAP, SQL and IMAP.")
            )

        runtime_group.add_option(
                "-l",
                dest    = "loglevel",
                type    = 'str',
                default = "CRITICAL",
                help    = _("Set the logging level. " + \
                            "One of info, warn, error, " + \
                            "critical or debug")
            )

        runtime_group.add_option(
                "-q", "--quiet",
                dest    = "quiet",
                action  = "store_true",
                default = False,
                help    = _("Be quiet.")
            )

        runtime_group.add_option(
                "-y", "--yes",
                dest    = "answer_yes",
                action  = "store_true",
                default = False,
                help    = _("Answer yes to all yes or no questions.")
            )

        self.cli_parser.add_option_group(runtime_group)

    def add_cli_parser_option_group(self, name):
        group = OptionGroup(self.cli_parser, name)
        return self.cli_parser.add_option_group(group)

    def has_section(self, section):
        if not self.cfg_parser:
            self.read_config()

        return self.cfg_parser.has_section(section)

    def has_option(self, section, option):
        if not self.cfg_parser:
            self.read_config()

        return self.cfg_parser.has_option(section, option)

    def command_set(self, *args, **kw):
        """
            Set a configuration option.

            Pass me a section, key and value please. Note that the section should
            already exist.

            TODO: Add a strict parameter
            TODO: Add key value checking
        """

        if not self.cfg_parser:
            self.read_config()

        if not len(args) == 3:
            log.error(_("Insufficient options. Need section, key and value -in that order."))

        if not self.cfg_parser.has_section(args[0]):
            log.error(_("No section '%s' exists.") % (args[0]))

        if '%' in args[2]:
            value = args[2].replace('%', '%%')
        else:
            value = args[2]

        self.cfg_parser.set(args[0], args[1], value)

        if hasattr(self, 'cli_keywords') and hasattr(self.cli_keywords, 'config_file'):
            fp = open(self.cli_keywords.config_file, "w+")
            self.cfg_parser.write(fp)
            fp.close()
        else:
            fp = open(self.config_file, "w+")
            self.cfg_parser.write(fp)
            fp.close()

    def get(self, section, key, quiet=False):
        """
            Get a configuration option from our store, the configuration file,
            or an external source if we have some sort of function for it.

            TODO: Include getting the value from plugins through a hook.
        """
        retval = False

        if not self.cfg_parser:
            self.read_config()

        #log.debug(_("Obtaining value for section %r, key %r") % (section, key), level=8)

        if self.cfg_parser.has_option(section, key):
            try:
                return self.cfg_parser.get(section, key)
            except:
                self.read_config()
                return self.cfg_parser.get(section, key)

        if hasattr(self, "get_%s_%s" % (section,key)):
            try:
                exec("retval = self.get_%s_%s(quiet)" % (section,key))
            except Exception, e:
                log.error(_("Could not execute configuration function: %s") % ("get_%s_%s(quiet=%r)" % (section,key,quiet)))
                return None

            return retval

        if quiet:
            return ""
        else:
            if hasattr(self.defaults, "%s_%s" % (section,key)):
                return getattr(self.defaults, "%s_%s" % (section,key))
            elif hasattr(self.defaults, "%s" % (section)):
                if key in getattr(self.defaults, "%s" % (section)):
                    _dict = getattr(self.defaults, "%s" % (section))
                    return _dict[key]
                else:
                    return None
            else:
                return None

    def get_raw(self, section, key):
        if not self.cfg_parser:
            self.read_config()

        if self.cfg_parser.has_option(section, key):
            return self.cfg_parser.get(section,key, 1)

    def parse_args(self):
        (self.cli_keywords, self.cli_args) = self.cli_parser.parse_args()

        self.read_config()

        self.set_defaults_from_cli_options()

        # Also set the cli options
        if hasattr(self,'cli_keywords') and not self.cli_keywords == None:
            for option in self.cli_keywords.__dict__.keys():
                retval = False
                if hasattr(self, "check_setting_%s" % (option)):
                    exec("retval = self.check_setting_%s(%r)" % (option, self.cli_keywords.__dict__[option]))

                    # The warning, error or confirmation dialog is in the check_setting_%s() function
                    if not retval:
                        continue

                    log.debug(_("Setting %s to %r (from CLI, verified)") % (option, self.cli_keywords.__dict__[option]), level=8)
                    setattr(self,option,self.cli_keywords.__dict__[option])
                else:
                    log.debug(_("Setting %s to %r (from CLI, not checked)") % (option, self.cli_keywords.__dict__[option]), level=8)
                    setattr(self,option,self.cli_keywords.__dict__[option])

    def read_config(self, value=None):
        """
            Reads the configuration file, sets a self.cfg_parser.
        """

        if not value:
            if hasattr(self, 'cli_keywords') and not self.cli_keywords == None:
                value = self.cli_keywords.config_file

        self.cfg_parser = SafeConfigParser()
        self.cfg_parser.read(value)

        if hasattr(self, 'cli_keywords') and hasattr(self.cli_keywords, 'config_file'):
            self.cli_keywords.config_file = value

        self.config_file = value

    def set_defaults_from_cli_options(self):
        for long_opt in self.cli_parser.__dict__['_long_opt'].keys():
            if long_opt == "--help":
                continue
            setattr(self.defaults,self.cli_parser._long_opt[long_opt].dest,self.cli_parser._long_opt[long_opt].default)

        # But, they should be available in our class as well
        for option in self.cli_parser.defaults.keys():
            log.debug(_("Setting %s to %r (from the default values for CLI options)") % (option, self.cli_parser.defaults[option]), level=8)
            setattr(self,option,self.cli_parser.defaults[option])
