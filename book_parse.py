import os, re, sys

chapter_end = '\\n{6}([A-Z ]+)\\n{3}'
chapter_end_pattern = re.compile(chapter_end)

def int_to_roman(input):
    """ Convert an integer to a Roman numeral. """

    if not isinstance(input, type(1)):
        raise TypeError("expected integer, got %s" % type(input))
    if not 0 < input < 4000:
        raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
    nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
    result = []
    for i in range(len(ints)):
        count = int(input / ints[i])
        result.append(nums[i] * count)
        input -= ints[i] * count
    return ''.join(result)

def roman_to_int(input):
    """ Convert a Roman numeral to an integer. """

    if not isinstance(input, type("")):
        raise TypeError("expected string, got %s" % type(input))
    input = input.upper(  )
    nums = {'M':1000, 'D':500, 'C':100, 'L':50, 'X':10, 'V':5, 'I':1}
    sum = 0
    for i in range(len(input)):
        try:
            value = nums[input[i]]
            # If the next place holds a larger number, this value is negative
            if i+1 < len(input) and nums[input[i+1]] > value:
                sum -= value
            else: sum += value
        except KeyError:
            raise ValueError('input is not a valid Roman numeral: %s' % input)
    # easiest test for validity...
    if int_to_roman(sum) == input:
        return sum
    else:
        raise ValueError('input is not a valid Roman numeral: %s' % input)

def create_filename(chapter, dir):
    """
    Creates a filename in the form: chnum - POV instance.txt where chnum is the
    integer chapter number, POV is the character name and instance is the roman
    numeral instance of that POV character in the book.
    """

    # find chapters already saved with character's POV
    file_list = os.listdir(dir)
    chapters = [int(f[:2]) for f in file_list if f[3] == '-']
    try:
        chapter_num = max(chapters) + 1
    except ValueError:
        chapter_num = 1
    matches = [roman_to_int(f[f.find(chapter[0]) + len(chapter[0]) + 1:f.find('.txt')]) \
               for f in file_list if chapter[0] in f]

    # counting POV instances
    if len(matches) > 0:
        instance_number = max(matches) + 1
    else:
        instance_number = 1

    return '{0:0>2} - {1} {2}.txt'.format(
        chapter_num,
        chapter[0],
        int_to_roman(instance_number)
    )

def parse_chapter_names(text):

    result = chapter_end_pattern.finditer(text)
    chapter_info_list = []
    for ch_num, chapter in enumerate(result):
        if ch_num > 0:
            chapter_info_list[-1] = (chapter_info_list[-1][0], chapter_info_list[-1][1], chapter.start())
        chapter_info_list.append((chapter.group(1).title(), chapter.end(), -1))

    return chapter_info_list

def main(fn):
    with open(fn, 'r', encoding='utf-8') as f:
        contents = f.read()

    chapter_names = parse_chapter_names(contents)

    for chapter in chapter_names:
        filename = create_filename(chapter, fn[:fn.rfind('/')+1])
        filename = fn[:fn.rfind('/')+1] + filename

        text = contents[chapter[1]:chapter[2]]
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(text)

if __name__ == '__main__':
    # pass the filename here
    main(sys.argv[1])