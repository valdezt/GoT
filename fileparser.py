import re
import pandas as pd

regex_speaking_line = '(?P<character>[^()]*)(?P<space> )?(?P<action>\(.*\))?: (?P<speaking_line>.*)'
regex_action_line = '\[(?P<action>.*)\]'
# For actions that continue over multiple lines
regex_action_start_only = '\[(?P<action>.*)'
regex_action_end_only = '(?P<action>.*)\]'

rx_dict = {
    'action': re.compile(regex_action_line),
    'action_start': re.compile(regex_action_start_only),
    'action_end': re.compile(regex_action_end_only),
    'speaking': re.compile(regex_speaking_line)
}

def _parse_line(line):
    """
    Search a line against all defined regexes and return the key and match
    result of the first matching regex.
    """

    for key, rx in rx_dict.items():
        match = rx.search(line)
        if match:
            return key, match

    return None, None

def parse_file(filepath):
    """
    Parse a particular file.
    """

    data = []

    with open(filepath, 'r', encoding='utf8') as file_object:
        line = file_object.readline()
        while line:

            row = None
            key, match = _parse_line(line)
            action, speaking_line, character = None, None, None

            if key == 'speaking':
                speaking_line = match.group('speaking_line')
                character = match.group('character')
                row = {
                    'speaking_line' : speaking_line,
                    'character': character,
                    'action': ''
                }

            if key in ('action', 'action_start', 'action_end'):
                action = match.group('action')
                row = {
                    'speaking_line' : '',
                    'character': '',
                    'action' : action
                }

            if row:
                data.append(row)

            line = file_object.readline()

    data = pd.DataFrame(data)

    return data