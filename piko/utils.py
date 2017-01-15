"""
    piko.utils
    ==========

    Utilities for piko
"""
import getpass
import sys

import piko
from piko.translate import _

# pylint: disable=invalid-name
log = piko.getLogger('piko.utils')
conf = piko.getConf()


# pylint: disable=too-many-branches
def ask_question(question, default="", password=False, confirm=False):
    """
        Ask a question on stderr.

        Since the answer to the question may actually be a password, cover that
        case with a getpass.getpass() prompt.

        Accepts a default value, but ignores defaults for password prompts.

        .. rubric:: Usage

        >>> piko.utils.ask_question(
            "What is the server?",
            default="localhost"
        )
    """

    if not empty(default) and conf.cli_keywords.answer_default:
        if not conf.cli_keywords.quiet:
            # pylint: disable=superfluous-parens
            print("%s [%s]: " % (question, default))
        return default

    if password:
        if empty(default):
            answer = getpass.getpass("%s: " % (question))
        else:
            answer = getpass.getpass("%s [%s]: " % (question, default))
    else:
        if empty(default):
            answer = raw_input("%s: " % (question))
        else:
            answer = raw_input("%s [%s]: " % (question, default))

    # pylint: disable=too-many-nested-blocks
    if answer != "":
        if confirm:
            answer_confirm = None
            answer_confirmed = False

            while not answer_confirmed:
                if password:
                    answer_confirm = getpass.getpass(
                        _("Confirm %s: ") % (question)
                    )

                else:
                    answer_confirm = raw_input(_("Confirm %s: ") % (question))

                if answer_confirm != answer:
                    print >> sys.stderr, _("Incorrect confirmation. " +
                                           "Please try again.")

                    if password:
                        if empty(default):
                            answer = getpass.getpass(_("%s: ") % (question))
                        else:
                            answer = getpass.getpass(
                                _("%s [%s]: ") % (question, default)
                            )

                    else:
                        if empty(default):
                            answer = raw_input(_("%s: ") % (question))
                        else:
                            answer = raw_input(
                                _("%s [%s]: ") % (question, default)
                            )

                else:
                    answer_confirmed = True

    if answer == "":
        return default
    else:
        return answer


def empty(value):
    """
        See if :py:param:`value` is an empty string.
    """
    if value == "":
        return True

    if value is None:
        return True

    return False


def generate_hex_id():
    """
        Generate a hexadecimal using :py:func:`uuid.uuid4`.
    """
    from uuid import uuid4

    uuid = uuid4()

    return uuid.hex


def generate_int_id():
    """
        Generate an integer using :py:func:`uuid.uuid4`.

        This generates a random 128-bit integer, which is then converted
        to an integer that databases such as MariaDB might understand.
    """
    from uuid import uuid4

    uuid = uuid4()

    return (int)(uuid.__int__() / 2**97)


def generate_uuid():
    """
        Generate a unique ID using :py:func:`uuid.uuid4`.
    """
    from uuid import uuid4

    uuid = uuid4()

    return uuid.__str__()


def multiline_message(message):
    """
        Issue a multiline message.
    """
    if hasattr(conf, 'cli_keywords') and hasattr(conf.cli_keywords, 'quiet'):
        if conf.cli_keywords.quiet:
            return ""

    column_width = 80

    # First, replace all occurences of "\n"
    message = message.replace("    ", "")
    message = message.replace("\n", " ")

    lines = []
    line = ""
    for word in message.split():
        if (len(line) + len(word)) > column_width:
            lines.append(line)
            line = word
        else:
            if line == "":
                line = word
            else:
                line += " %s" % (word)

    lines.append(line)

    return "\n%s\n" % ("\n".join(lines))
