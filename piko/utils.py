import getpass

import piko

log = piko.getLogger('piko.utils')
conf = piko.getConf()

def ask_question(question, default="", password=False, confirm=False):
    """
        Ask a question on stderr.

        Since the answer to the question may actually be a password, cover that
        case with a getpass.getpass() prompt.

        Accepts a default value, but ignores defaults for password prompts.

        Usage: pykolab.utils.ask_question("What is the server?", default="localhost")
    """

    if not default == "" and not default == None and conf.cli_keywords.answer_default:
        if not conf.cli_keywords.quiet:
            print ("%s [%s]: " % (question, default))
        return default

    if password:
        if default == "" or default == None:
            answer = getpass.getpass("%s: " % (question))
        else:
            answer = getpass.getpass("%s [%s]: " % (question, default))
    else:
        if default == "" or default == None:
            answer = raw_input("%s: " % (question))
        else:
            answer = raw_input("%s [%s]: " % (question, default))

    if not answer == "":
        if confirm:
            answer_confirm = None
            answer_confirmed = False
            while not answer_confirmed:
                if password:
                    answer_confirm = getpass.getpass(_("Confirm %s: ") % (question))
                else:
                    answer_confirm = raw_input(_("Confirm %s: ") % (question))

                if not answer_confirm == answer:
                    print >> sys.stderr, _("Incorrect confirmation. " + \
                            "Please try again.")

                    if password:
                        if default == "" or default == None:
                            answer = getpass.getpass(_("%s: ") % (question))
                        else:
                            answer = getpass.getpass(_("%s [%s]: ") % (question, default))
                    else:
                        if default == "" or default == None:
                            answer = raw_input(_("%s: ") % (question))
                        else:
                            answer = raw_input(_("%s [%s]: ") % (question, default))

                else:
                    answer_confirmed = True

    if answer == "":
        return default
    else:
        return answer

def multiline_message(message):
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


