
def resize_proportional(width, height, width_max, height_max=None):
    width = float(width)
    height = float(height)
    if width > width_max:
        height *= width_max/width
        width  *= width_max/width
    if height_max is not None and height > height_max:
        width  *= height_max/height
        height *= height_max/height
    return int(round(width)), int(round(height))

def split_words(s):
    '''
    Split words like MongoDB does.

    Examples:
      'abc'           => ['abc']
      'abc def'       => ['abc', 'def']
      'abc    def '   => ['abc', 'def']
      ' "foo   bar "' => ['foo   bar ']
      ' foo" bar '    => ['foo', ' bar ']
    '''

    words = []
    word = ''
    in_quote = False
    for c in s:
        if in_quote:
            if c == '"':
                in_quote = False
                if word:
                    words.append(word)
                    word = ''
            else:
                word += c
        else:
            if c == '"' or c == ' ':
                if c == '"':
                    in_quote = True
                word = word.strip()
                if word:
                    words.append(word)
                    word = ''
            else:
                word += c

    if in_quote:
        if word:
            words.append(word)
    else:
        word = word.strip()
        if word:
            words.append(word)

    return words



# vim: et:sta:bs=2:sw=4:
