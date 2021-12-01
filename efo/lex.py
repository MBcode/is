import sys

COMMA = ','
SPACE = ' '


#def uninvert(s):
def uninvert(st):
    """
    Recursively uninverts a string. I.e., injury, abdominal ==> abdominal injury

    Translated directly from uninvert(s,t) in lex.c.

    @param s INPUT: string "s" containing the term to be uninverted.
    @return OUTPUT: string containing the uninverted string.

    """
    #if isinstance(st, str):
    if not isinstance(st, str):
        #s=st.encode('utf-8')
        s=st.decode('utf-8')
        print(f'not-str:{st}')
    else:
        s=st
        print(f'{st}')
    if len(s) == 0:
        return s
    #s=st #skip above
    sp = s.find(COMMA)
    while sp > 0:
        cp = sp
        cp+=1
        if cp < len(s) and s[cp] == SPACE:
            while cp < len(s) and s[cp] == SPACE:
                cp+=1
            return uninvert(s[cp:]) + " " + s[0:sp].strip()
        else:
            sp+=1
        sp = s.find(COMMA, sp)
    return s.strip();

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(('%s -> %s' % (sys.argv[1], uninvert(sys.argv[1]))))
