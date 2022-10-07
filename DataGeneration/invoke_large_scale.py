# Large Scale Test
# This is to generate invoke commands to execute SMT solution and heuristic approaches
from subprocess import Popen
from itertools import islice

# for small scale scenario, the maximum number of RBs, here we use pilots
max_pilots = 5

# Are SMT and Heuristic available?
is_SMT = 0
is_Heuristic = 0
is_Theoretical = 1

# storing the generated commands
commands_SMT = []
commands_Heuristic = []
commands_Theoretical = []

# for large scale scenario, 'COmax' equals algorithm 'CoU' while '1' equals algorithm 'Co1'
confname = ['COmax', '1']

# for large scale scenario, we set up a sufficiently large number of RBs
nopilotsH = 200
# represent different number of traffic flows
folder_name = ['10', '20', '30', '40', '50', '60', '70']


# generate commands for "Co1"
def generate_commands_H_1(whichfolder):
    with open('application_info/applications_large_scale_%d.txt' % int(folder_name[whichfolder]), 'r') as f:
        lines = f.readlines()
        for current_count in range(len(lines)):
            # parse the information
            l = lines[current_count].strip('\n').strip(' ').split(' ')
            # meta info
            nrofTF = int(l[0])
            hp = int(l[1])

            # Commands for Heuristic Approach
            heu_command = 'python ../Heuristic/BasicHeuristic_optimizing_1.py %d %d %d %d %d %d ' % \
                          (current_count, 1, nrofTF, nopilotsH, hp, whichfolder)

            for tf in range(nrofTF):
                offset = int(l[tf * 6 + 2])
                transmission_period = int(l[tf * 6 + 3])
                payload = int(l[tf * 6 + 4])
                latency = int(l[tf * 6 + 5])
                # confs = int(l[tf * 6 + 6])
                confs = 1

                co = int(float(l[tf * 6 + 7]))
                heu_command += ' %d %d %d %d %d %d' % (offset, transmission_period, payload, latency, confs, co)
            # print(heu_command)
            commands_Heuristic.append(heu_command)


# generate commands for "CoU"
def generate_commands_H_nolimitation(whichfolder):
    with open('application_info/applications_large_scale_%d.txt' % int(folder_name[whichfolder]), 'r') as f:
        lines = f.readlines()
        for current_count in range(len(lines)):
            # parse the information
            l = lines[current_count].strip('\n').strip(' ').split(' ')
            # meta info
            nrofTF = int(l[0])
            hp = int(l[1])

            # Commands for Heuristic Approach
            heu_command = 'python ../Heuristic/BasicHeuristic_optimizing.py %d %d %d %d %d %d ' % \
                          (current_count, 0, nrofTF, nopilotsH, hp, whichfolder)

            for tf in range(nrofTF):
                offset = int(l[tf * 6 + 2])
                transmission_period = int(l[tf * 6 + 3])
                payload = int(l[tf * 6 + 4])
                latency = int(l[tf * 6 + 5])
                confs = int(l[tf * 6 + 6])
                co = int(float(l[tf * 6 + 7]))
                heu_command += ' %d %d %d %d %d %d' % (offset, transmission_period, payload, latency, confs, co)
            commands_Heuristic.append(heu_command)


# generate commands for "FCFS"
def generate_commands_T(whichfolder):
    with open('application_info/applications_large_scale_%d.txt' % int(folder_name[whichfolder]), 'r') as f:
        lines = f.readlines()
        for current_count in range(len(lines)):
            # parse the information
            l = lines[current_count].strip('\n').strip(' ').split(' ')
            # meta info
            nrofTF = int(l[0])
            hp = int(l[1])

            # Commands for Theoretical analysis
            nav_command = 'python ../NaiveApproach/naive.py %d %d %d %d %d %d ' % \
                          (current_count, 0, nrofTF, nopilotsH, hp, whichfolder)
            for tf in range(nrofTF):
                offset = int(l[tf * 6 + 2])
                transmission_period = int(l[tf * 6 + 3])
                payload = int(l[tf * 6 + 4])
                latency = int(l[tf * 6 + 5])
                confs = 1
                co = int(float(l[tf * 6 + 7]))
                nav_command += ' %d %d %d %d %d %d' % (offset, transmission_period, payload, latency, confs, co)
            commands_Theoretical.append(nav_command)


# for different number of traffic flows, perform "Co1", "CoU", and "FCFS"
for i in range(len(folder_name)):
    if is_Heuristic:
        generate_commands_H_nolimitation(i)
        generate_commands_H_1(i)
    if is_Theoretical:
        generate_commands_T(i)

if is_Heuristic:
    max_workers = 6  # no more than 6 concurrent processes
    processes = (Popen(cmd, shell=True) for cmd in commands_Heuristic)
    running_processes = list(islice(processes, max_workers))  # start new processes
    while running_processes:
        for i, process in enumerate(running_processes):
            if process.poll() is not None:  # the process has finished
                running_processes[i] = next(processes, None)  # start new process
                if running_processes[i] is None:  # no new processes
                    del running_processes[i]
                    break

    # SMT...
if is_SMT:
    max_workers = 6  # no more than 6 concurrent processes
    processes = (Popen(cmd, shell=True) for cmd in commands_SMT)
    running_processes = list(islice(processes, max_workers))  # start new processes
    while running_processes:
        for i, process in enumerate(running_processes):
            if process.poll() is not None:  # the process has finished
                running_processes[i] = next(processes, None)  # start new process
                if running_processes[i] is None:  # no new processes
                    del running_processes[i]
                    break

if is_Theoretical:
    max_workers = 6  # no more than 6 concurrent processes
    processes = (Popen(cmd, shell=True) for cmd in commands_Theoretical)
    running_processes = list(islice(processes, max_workers))  # start new processes
    while running_processes:
        for i, process in enumerate(running_processes):
            if process.poll() is not None:  # the process has finished
                running_processes[i] = next(processes, None)  # start new process
                if running_processes[i] is None:  # no new processes
                    del running_processes[i]
                    break
