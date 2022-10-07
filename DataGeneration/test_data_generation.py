# This is for generating traffic flows info that is suitable for the input of proposed algorithms.
# Many preparations have been finished, such as offset, # of resource units.
# Each file contains the information of multiple traffic flows.

from application_parameter_large_scale import *

# define the maximum number of test cases
MAX_COUNT = 10
# different number of traffic flows
folder_name = ['10', '20', '30', '40', '50', '60', '70']

for whichfolder in range(len(folder_name)):
    count = 0
    file = open('application_info/applications_large_scale_%s.txt' % (folder_name[whichfolder]), 'w')
    # format of each record
    # [number of applications, hyper period,
    # (offset, transmission period, payload, latency, number of packets, control overhead), (), ()]

    max_applications = int(folder_name[whichfolder])
    while count < MAX_COUNT:
        hp, list_applications = generating_application_info(max_applications)
        ss = ''
        ss += '%d %d ' % (max_applications, hp)
        for i in range(len(list_applications)):
            # offset, transmission period, payload, latency, number of packets, control overhead
            ss += '%d %d %d %d %d %d ' % (list_applications[i][0],
                                          list_applications[i][1],
                                          list_applications[i][2],
                                          list_applications[i][3],
                                          list_applications[i][4],
                                          list_applications[i][5])
        print(ss, file=file)

        count += 1