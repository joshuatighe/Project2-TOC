import csv
import sys

# get command line arguments: filename of TM, input string, and max_depth
try:
    filename = sys.argv[1]
    input_string = sys.argv[2]
    max_depth = int(sys.argv[3])
except IndexError:
    print('missing arguments')
    print(f'python traceTM_JT.py <filename> <input_string> <max_depth>')
    sys.exit(1)
except ValueError:
    print('max_depth must be an integer.')
    sys.exit(1)

with open(filename, newline='') as csvfile:
    csvreader = csv.reader(csvfile)

    # get headers of TM
    machine_name = next(csvreader)[0]
    next(csvreader)  # ignore Q
    next(csvreader)  # ignore epsilon
    next(csvreader)  # ignore gamma
    start_state = next(csvreader)[0]
    accept_state = next(csvreader)[0]
    reject_state = next(csvreader)[0]

    transitions = []

    # get all TM transitions
    for row in csvreader:
        current_state, current_char, next_state, write_char, direction = row
        transitions.append({
            'current_state': current_state,
            'current_char': current_char,
            'next_state': next_state,
            'write_char': write_char,
            'direction': direction
        })

depth = 0
total_transitions = 0

accepted = False

# left, current state, right
starting_config = ['', start_state, input_string]

# first level of tree is just the starting configuration
tree = [[starting_config]]

while depth < max_depth:
    next_depth_configs = []

    # check if all configs are in reject
    all_rejected = True

    for config in tree[depth]:
        if config[1] != reject_state:
            all_rejected = False

    if all_rejected:
        break

    # loop through all configs at current depth
    for config in tree[depth]:
        if config[1] == accept_state:
            accepted = True
            break

        if config[1] == reject_state:
            continue

        # get char at head
        head_char = config[2][0] if len(config[2]) > 0 else ''

        # get valid transitions for current config
        valid_transitions = []
        for transition in transitions:
            if transition['current_state'] == config[1] and transition['current_char'] == head_char:
                valid_transitions.append(transition)

        # no valid transitions, implicit reject
        if not valid_transitions:
            next_depth_configs.append([config[0], reject_state, config[2]])
            total_transitions += 1
            
            continue
        
        # append valid transitions to next_depth_configs
        for transition in valid_transitions:
            write_char = transition['write_char']
            new_state = transition['next_state']

            # new config depends on direction of tape
            if transition['direction'] == 'R':
                new_left = config[0] + write_char
                new_right = config[2][1:] if len(config[2]) > 1 else '_'
            else:
                new_left = config[0][:-1] if len(config[0]) > 1 else ''
                new_right = config[0][-1] + write_char + config[2][1:]

            next_depth_configs.append([new_left, new_state, new_right])
            total_transitions += 1

    if accepted:
        break

    tree.append(next_depth_configs)
    depth += 1

# check for acceptance in last level of tree (edge case)
if not accepted:
    for config in tree[-1]:
        if config[1] == accept_state:
            accepted = True
            break

# print results
print(f'Machine Name: {machine_name}')
print(f'Initial String: {input_string}')
print(f'Configuration Tree Depth: {depth}')
print(f'Total Transitions Simulated: {total_transitions}')
print()

if accepted:  # accepted string found, depth = no. of transitions it took to get there
    print(f'String accepted in {depth} transitions')
    print('Configuration path:')
elif not all_rejected:  # execution stopped early due to max_depth being reached
    print(f'Execution stopped after reaching max tree depth: {max_depth}')
else:  # all configs rejected at depth
    print(f'All configs rejected at a depth of {depth}')

# print tree
for level in tree:
    print(level)