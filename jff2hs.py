# jflap turing machine to haskell converter
# by robert usher
# http://dcc.nitrated.net/ 

from lxml import etree
from sys import argv

# expect filename to be argv[1]
tree    = etree.parse(argv[1])

machine = {}
initial = False

for element in tree.getroot():
    # is this actually a turing machine?
    if element.tag == 'type' and element.text != 'turing':
        print error 
        break
    
    # we want the machine!
    if element.tag == 'automaton':
        automaton = element
        
for child in automaton:
    # we get the list of states
    if child.tag == 'block':
        if not initial:
            for r in child:
                if r.tag == 'initial':
                    initial = int(child.get('id'))
                    break
                    
        machine[child.get('id')] = {'name' : child.get('name'), 'transitions' : []}
        
    # list of transitions
    if child.tag == 'transition':
        transition = {}
        source = False
        
        for r in child:
            # record the source state
            if r.tag == 'from':
                source = r.text
                continue
                
            transition[r.tag] = r.text
           
        # add this transition to the source state's transition list
        machine[source]['transitions'].append(transition)

# need to map the JFLAP state ids to our new representation
states = { initial: 1 }
next = 2

# now we output the haskell forma
print 'module T where'
print 
print 'import Turing'
print 
print 't :: Turing_Machine'
print 't = ['

o = { 0 : "\t\t-- State 0\n\
\t\t[ (' ', (1, ' ', R))\n \
\t\t]"}
    
todo = [initial]

while len(todo) > 0:    
    current = int(todo.pop())
    s = []

    for transition in machine[str(current)]['transitions']:
        # have we got a name for this new state?
        to = int(transition['to'])
        
        if to not in states:
            states[to] = next
            todo.append(to)
            next += 1
        
        read = transition['read']
        write = transition['write']
        move = transition['move']
        
        if read is None:
            read = ' '
            
        if write is None:
            write = ' '
        
        # what does the transition look like?    
        s.append("\t\t\t('" + read + "', (" + str(states[to]) + ", '" + write + "', " + move + "))")

    t = '\t\t-- State ' + str(states[current]) + " (" + str(current) + ")\n\t\t[\n"
    t += ',\n'.join(s) + "\n\t\t]"
    
    o[states[current]] = t

for i in range (0, next):
    print o[i],
    if (i != next - 1):
        print ',',
    print '\n'
    
print ' ]'