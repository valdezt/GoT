import re
import pandas as pd

regex_speaking_line = '(?P<character>[^():]*)(?P<space_1> )?(?P<direction>\(.*\))?:(?P<space_2> +)(?P<speaking_line>.*)'
regex_speaking_line_2 = '(?P<character>[^():]*):(?P<space_1> +)?(?P<direction>\(.*\))?(?P<space_2> +)(?P<speaking_line>.*)'
regex_action_line = '\[(?P<action>.*)\]'
# For actions that continue over multiple lines
regex_action_start_only = '\[(?P<action>.*)'
regex_action_end_only = '(?P<action>.*)\]'
regex_lazy_action = '(?P<action>.*)'

regex_season_episode_parse = '.*[season](?P<season>\d).*[e](?P<episode>\d).*'
rx_sep = re.compile(regex_season_episode_parse)

rx_dict = {
    'action': re.compile(regex_action_line),
    'action_start': re.compile(regex_action_start_only),
    'action_end': re.compile(regex_action_end_only),
    'speaking': re.compile(regex_speaking_line),
    'lazy_action': re.compile(regex_lazy_action)
}

# This dictionary will help convert names of characters from first name only
# to first + last name.
character_dictionary = {
    'Arya' : 'Arya Stark',
    'Barriston' : 'Barristan Selmy',
    'Benjen' : 'Benjen Stark',
    'Catelyn' : 'Catelyn Stark',
    'Cersei' : 'Cersei Lannister',
    'Bran' : 'Bran Stark',
    'Daenerys' : 'Daenerys Targaryen',
    'Illyrio' : 'Illyrio Mopatis',
    'Jaime' : 'Jaime Lannister',
    'Jon' : 'Jon Snow',
    'Jorah' : 'Jorah Mormont',
    'Luwin' : 'Maester Luwin',
    'Ned' : 'Eddard Stark',
    'Ned Stark' : 'Eddard Stark',
    'Robb' : 'Robb Stark',
    'Robert' : 'Robert Baratheon',
    'Sansa' : 'Sansa Stark',
    'The Hound' : 'Sandor Clegane',
    'Theon' : 'Theon Greyjoy',
    'Tyrion' : 'Tyrion Lannister',
    'Viserys' : 'Viserys Targaryen'
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

        episode_index = rx_sep.search(filepath)
        season = episode_index.group('season')
        episode = episode_index.group('episode')

        line = file_object.readline()
        while line:

            row = None
            key, match = _parse_line(line)
            action, speaking_line, character = None, None, None

            if key == 'speaking':
                speaking_line = match.group('speaking_line')
                character = match.group('character')
                direction = match.group('direction')
                row = {
                    'speaking_line' : speaking_line,
                    'character': character,
                    'action': '',
                    'direction': direction,
                    'season': season,
                    'episode': episode
                }

            if key in ('action', 'action_start', 'action_end', 'lazy_action'):
                action = match.group('action')
                row = {
                    'speaking_line' : '',
                    'character': '',
                    'action' : action,
                    'direction': '',
                    'season': season,
                    'episode': episode
                }

            if row:
                data.append(row)

            line = file_object.readline()

    data = pd.DataFrame(data)

    return data

def convert_character(x):
    x = x.lower().title().strip()

    try:
        return character_dictionary[x]
    except KeyError:
        return x

def parse_season(season_number, max_episode_number):

    df = pd.DataFrame(
        columns=[
            'speaking_line',
            'character',
            'action',
            'direction',
            'season',
            'episode'
        ]
    )

    for episode_number in range(1, max_episode_number+1):
        filepath = f'./Data/season{season_number}/e{episode_number}.txt'
        df = df.append(parse_file(filepath))

    return df