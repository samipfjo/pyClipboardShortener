# wwparser.py
#   Configuration file parser
#   Luke Jones, 2016
# ------


def parse(file='config.ini'):
    """
    Parse a configuration file.
    At this point I don't even vaguely remember the syntax,
    too lazy to re-read code. This is SUPER hacky and exploits
    all sorts of fun Python dict quirks
    """
    
    with open(file) as f:
        count = 0
        
        nest_stack = []
        pos_stack = []
        
        store = {}
        pos = store  # pointer to our location in the store
        
        for line in f.readlines():
            line = line.strip()
            
            if len(line) == 0 or line[0] in ['#', '\n']:  # Skip comments and blank lines
                continue

            # Set our position back to the beginning of the store and
            # prep for new entries
            if line[0] == '[':
                if len(pos_stack) != 0:
                    pos_stack.clear()
                    del pos
                    pos = store
                
                head = line[1:-1]
                pos[head] = {}
                pos_stack.append(pos)
                pos = pos[head]


            # Add a dict on this level; treat as a value rather than as a structure
            elif line[:2] == '&[':
                head = line[2:-1]

                if len(nest_stack) != 0 and nest_stack[-1] == '&[':
                    pos = pos_stack.pop()
                    nest_stack.pop()
  
                pos[head] = {}
                pos = pos[head]
                

            # Add a new dict layer
            elif line[:2] == '^[':
                head = line[2:-1]
                pos[head] = {}
                pos_stack.append(pos)
                pos = pos[head]


            # Back out one layer
            elif line[:2] == '.[':
                head = line[2:-1]

                if len(nest_stack) != 0 and nest_stack[-1] == '&[':
                    nest_stack.pop()

                pos = pos_stack.pop()
                pos[head] = {}
                pos = pos[head]


            else:
                try:
                    keyval = line.replace(' ', '')  # Handle this better in the future...
                    key, value = keyval.split(':')  # Retrieve keyval store
                    pos[key] = value

                except ValueError:
                    raise SyntaxError('Cannot process line {}, "{}"'.format(count, line))

            count += 1
                    
    return store
        

if __name__ == '__main__':
    print(parse())
    