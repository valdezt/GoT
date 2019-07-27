import re
import pandas as pd
from characters import character_dictionary

regex_speaking_line = '(?P<character>[^():]*)(?P<space_1> )?(?P<direction>\(.*\))?:(?P<space_2> +)(?P<speaking_line>.*)'
regex_speaking_direction = '(?P<direction>\([^():]*\))?\.?\ ?(?P<speaking_line>[^():]*) ?'

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

rx_speaking_direction = re.compile(regex_speaking_direction)

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

def _parse_speaking_line(speaking_line):
    """
    In some instances, speaking lines contain multiple iterations of:
    (direction) speech
    For instance:
    JOFFREY: (Quietly) Well struck… (Louder) Well struck, Dog.
    This function will parse the speaking line (everything after 'JOFFREY: ') to
    retrieve the multiple sets of speech/direction pairs.
    """

    return rx_speaking_direction.findall(speaking_line)

def _convert_character(x):
    x = x.lower().strip()

    try:
        return character_dictionary[x]
    except KeyError:
        return x

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

            rows = None
            key, match = _parse_line(line)
            action, speaking_line, character, direction = None, None, None, None

            if key == 'speaking':
                speaking_lines = _parse_speaking_line(match.group('speaking_line'))[:-1]
                character = match.group('character')
                direction = match.group('direction')

                rows = [
                    {
                        'speaking_line' : speaking_line[1],
                        'character': character,
                        'action': '',
                        'direction': speaking_line[0] if speaking_line[0] != '' else (direction or ''),
                        'season': season,
                        'episode': episode
                    }
                    for speaking_line in speaking_lines
                ]

            if key in ('action', 'action_start', 'action_end', 'lazy_action'):
                action = match.group('action')
                rows = [
                    {
                        'speaking_line' : '',
                        'character': '',
                        'action' : action,
                        'direction': '',
                        'season': season,
                        'episode': episode
                    }
                ]

            if rows:
                for row in rows:
                    data.append(row)

            line = file_object.readline()

    data = pd.DataFrame(data)

    return _clean_dataframe(data)

def _clean_dataframe(df):
    """
    Cleans the GoT script dataframe.
    """

    df['character'] = df.character.apply(lambda x: _convert_character(x))
    df['speaking_line'] = df.speaking_line.apply(lambda x: x.lower().strip())
    df['action'] = df.action.apply(lambda x: x.lower())
    df['direction'] = df.direction.apply(lambda x: x.lower())

    return df

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
        filepath = f'./showdata/season{season_number}/e{episode_number}.txt'
        df = df.append(parse_file(filepath))

    # cleaning functions
    return df