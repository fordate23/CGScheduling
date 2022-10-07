import numpy as np
import math
import sys

sys.path.append('../DataGeneration/')
# from DataGeneration.invoke import confname
# from DataGeneration.application_parameter import hyper_period

# threshold when generating shape alternatives
allowedAdditionalRB = 3
from datetime import datetime
import sys
# rectifiedWidth_factor = 1

# 0: COmax
# 1: 0.5COmax
# 2: 50
# 3: 20
# 4: 15
# 5: 10
# 6: 5
# 7: 2
# 8: 1
# confname = ['COmax', '0.5COmax', '50', '20', '15','10', '5', '2', '1']
confname = ['COmax', '1']
folder_name = ['10', '20', '30', '40', '50', '60', '70', '80']

# distance between offset
# distance_control_payload = 50

# symbol used to separate control and data
interval_data_control = 9999

# from meta_configuration import *

timeSystemStart = datetime.now()

# This aims to implement a basic prototype for solving the resource scheduling problem.

# First Step: define traffic flow: 0 initial time 1 transmission period   2 payload   3 latency

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))
arguments = sys.argv
# arguments = ['~', '0', '0', '4', '6', '20',
#              '1', '5', '3', '3', '4', '2',
#              '0', '2', '2', '2', '10', '2',
#              '0', '4', '2', '3', '5', '2',
#              '1', '4', '2', '3', '5', '2']

#
# arguments = ['../Heuristic/BasicHeuristic_optimizing.py', '0', '8', '20', '45', '1680',
#              '0', '16', '2', '8', '1', '5',
#              '0', '8', '1', '4', '1', '3',
#              '0', '12', '1', '5', '1', '3',
#              '0', '14', '1', '8', '1', '3',
#              '0', '14', '1', '5', '1', '3',
#              '0', '14', '1', '8', '1', '3',
#              '0', '14', '1', '7', '1', '3',
#              '0', '4', '1', '1', '1', '3',
#              '0', '4', '1', '2', '1', '3',
#              '0', '6', '1', '3', '1', '3',
#              '0', '4', '1', '1', '1', '3',
#              '0', '14', '1', '6', '1', '3',
#              '0', '10', '1', '4', '1', '3',
#              '0', '10', '1', '4', '1', '3',
#              '0', '16', '1', '6', '1', '3',
#              '0', '12', '1', '6', '1', '3',
#              '0', '14', '2', '6', '1', '5',
#              '0', '4', '1', '2', '1', '5',
#              '0', '8', '1', '4', '1', '3',
#              '0', '10', '2', '4', '1', '5']

# format: command, series, number of tfs, pilots, hyper-period
# arguments = ['~', '0', '2', '6', '10',
#              '1', '5', '2', '3', '2', '2',
#              '0', '2', '2', '2', '5', '2']

# arguments = ['~', '0', '3', '10', '20',
#              '1', '5', '2', '3', '4', '2',
#              '0', '2', '2', '2', '10', '2',
#              '0', '4', '4', '3', '5', '2']

# arguments = ['~', '33', '3', '10', '20',
#              '1', '5', '2', '3', '4', '2',
#              '0', '2', '2', '2', '5', '2',
#              '0', '4', '4', '3', '5', '2']
# offset, transmission period, payload, latency, no. of configurations, RBs for control overhead
# ==================================== Read settings from invoke.py =======================
# nrof Series
noseries = int(arguments[1])
# index of numeber of conf's name
noconfname = int(arguments[2])
# INPUT: the information for traffic flows
numberoftfs = int(arguments[3])
# number of max pilots
nopilots = int(arguments[4])
# hyper-period
hyper_period = int(arguments[5])
# whichfolder
whichfolder = int(arguments[6])

log = open('../NaiveApproach/results/%d.txt' % noseries, 'w')
log_solvingtime = open('../NaiveApproach/a/solvingtime_%d.txt' % int(folder_name[whichfolder]), 'a')
log_pilots = open('../NaiveApproach/a/naive_%d.txt' % int(folder_name[whichfolder]), 'a')
log_heatmap = open('../NaiveApproach/a/heatmap_%s.txt' % (int(folder_name[whichfolder])), 'a')


class TF:
    # list of functions
    def __init__(self, initial_time, transmission_period, payload, delay_req, numberofconf, con_overhead, number):
        self.initial_time = initial_time
        self.transmission_period = transmission_period
        self.payload = payload
        self.delay_requirement = delay_req
        self.numberofconfigurations = 1  # max configurations (BS)
        self.control_overhead = con_overhead  # RBs for control overhead
        self.number = number  # for denoting each traffic flow, no functionality, for debug
        self.ratiopayloadtransmissionperid = self.payload / self.delay_requirement
        self.shapelist = []
        self.generate_alternatives()  # generate all shapes for a certain payload
        self.control_message_width = 1  # this value is given according to problem setting
        self.control_message_height = con_overhead
        self.scheduling_info = []  # for control, record all scheduling info (rectangle)
        self.numberofconfigurations_actual = -1  # after having scheduling info, the actual configurations
        self.offset_configurations_actual = []  # for limiting position of control message
        self.tmp_scheduling_info = []  # store the initial best-fit scheduling info
        self.scheduling_interval = []  # to know the start time and end time of each interval

    def __str__(self):
        return 'Initial time: %d, ' \
               'transmission period: %d, ' \
               'payload: %d RBs, ' \
               'delay requirement: %d, ' \
               'number of configurations: %d, ' \
               'RBs for control: %d' % \
               (self.initial_time,
                self.transmission_period,
                self.payload,
                self.delay_requirement,
                self.numberofconfigurations,
                self.control_overhead)

    # Function1: generate alternative shapes:
    # 1) list all possible cases for the current payload
    # 2) define a threshold, to enable more alternatives with acceptable cost
    def generate_alternatives(self):
        # for i in range(allowedAdditionalRB + 1):
        #     current_payload = self.payload + i
        #     # search for all alternatives
        #     biggest_width = int(rectifiedWidth_factor * min(current_payload, self.delay_requirement))
        #     for width in range(1, biggest_width + 1):
        #         if current_payload % width == 0:
        #             self.shapelist.append([width, int(current_payload / width)])
        # # self.shapelist = sorted(self.shapelist, key=lambda x: x[0], reverse=True)
        # at least find a shape like square, 2*2, 3*3, 4*4, 5*5...
        square_max = min(allowedAdditionalRB+self.payload, int(math.pow(math.ceil(math.sqrt(self.payload)), 2)))
        for target_payload in range(self.payload, square_max + 1):
            for width in range(1, int(self.delay_requirement) + 1):
                if target_payload % width == 0:
                    self.shapelist.append([width, int(target_payload / width)])
        # print('payload: %d' % self.payload)
        # print('Shape list:')
        # print(self.shapelist)


    def naivescheduling(self, rg):
        new_configuration_list = [[0, int(hyper_period/self.transmission_period)]]
        for index in range(len(new_configuration_list)):
            # for each configuration, calculate [offset, periodicity, width, height, bottom]
            # OPTIMIZATION here to generate new configuration information
            start_conf_index = new_configuration_list[index][0]
            number_of_packets = new_configuration_list[index][1]
            if number_of_packets == 0:
                continue
            # define the search space
            offset_ = self.scheduling_interval[start_conf_index][0]
            # for all shape, select the widest one
            # print(self)
            # print('Shape list: 1')
            # print(self.shapelist)
            shapelist = [x for x in self.shapelist if x[0]<= self.delay_requirement]
            # print('Shape list: 2')
            # print(shapelist)
            shapelist = sorted(shapelist, key=lambda x: x[0], reverse=True)
            # print('Shape list: 3')
            # print(shapelist)
            widest = shapelist[0]


            tp_ = self.transmission_period
            width_ = widest[0]
            height_ = widest[1]
            bottom_ = 0

            # generate all scheduling info for each data packet
            new_scheduling_info = []
            # element format: [l, r, b, h]
            for packets in range(number_of_packets):
                # for each packet
                new_scheduling_info.append([int(offset_ + tp_ * packets),
                                            int(offset_ + tp_ * packets + width_ - 1),
                                            int(bottom_),
                                            int(height_)])

                # check: resource collision with current resource grid
            while True:
                success_flag = True
                for packet_info_index in range(len(new_scheduling_info)):
                    left = new_scheduling_info[packet_info_index][0]
                    right = new_scheduling_info[packet_info_index][1]
                    bottom = new_scheduling_info[packet_info_index][2]
                    height = new_scheduling_info[packet_info_index][3]
                    # check max pilot constraint for avoiding out of bound
                    if bottom + height > nopilots:
                        print('No solution, fail!  1')
                        return -1

                    for col in range(left, right + 1):
                        for row in range(bottom, bottom + height):
                            try:
                                if rg.data[col][row] != -1:
                                    # print('collision!')
                                    success_flag = False
                            except:
                                print('Row: %d  Col: %d' % (row, col))
                                print(new_scheduling_info)
                if success_flag:
                    break
                else:
                    # update scheduling info: increment 'bottom' by 1
                    for ele in new_scheduling_info:
                        ele[2] += 1

            for packet_info_index in range(len(new_scheduling_info)):
                left = new_scheduling_info[packet_info_index][0]
                right = new_scheduling_info[packet_info_index][1]
                bottom = new_scheduling_info[packet_info_index][2]
                height = new_scheduling_info[packet_info_index][3]

                for col in range(left, right + 1):
                    for row in range(bottom, bottom + height):
                        rg.data[col][row] = self.number



# Store the traffic flows
TFlist = []

# fill in the above list using the parameters from 'arguments'
# number of attributes
number_attributes = 6
# reading offset
reading_offset = 6

for i in range(numberoftfs):
    initial_time_ = float(arguments[i * number_attributes + reading_offset + 1])
    transmission_period_ = float(arguments[i * number_attributes + reading_offset + 2])
    payload_ = int(float(arguments[i * number_attributes + reading_offset + 3]))
    latency_ = float(arguments[i * number_attributes + reading_offset + 4])
    numberofconf = int(float(arguments[i * number_attributes + reading_offset + 5]))
    control_overhead = int(float(arguments[i * number_attributes + reading_offset + 6]))

    # if 1/2 COmax
    # numberofconf = max(1, int(numberofconf / 2))
    # numberofconf = 1

    # print('number of configuration: %d' % numberofconf)
    # print('%d %d %d %d %d' % (initial_time_, transmission_period_, payload_, latency_, numberofconf))
    TFlist.append(TF(initial_time=initial_time_,
                     transmission_period=transmission_period_,
                     payload=payload_,
                     delay_req=latency_,
                     numberofconf=numberofconf,
                     con_overhead=control_overhead,
                     number=i))

numberofslots = hyper_period


class ResourceGrid:
    def __init__(self, slots, pilots):
        self.timeslots = slots
        self.pilots = pilots
        self.data = []
        for col in range(slots):
            tmp = []
            for row in range(pilots):
                tmp.append(-1)
            self.data.append(tmp)

    def __str__(self):
        return 'Resource Grid: %d * %d' % (self.timeslots, self.pilots)

    def update(self, left, right, bottom, height, tfno):
        for col in range(left, right + 1):
            for row in range(bottom, bottom + height):
                self.data[col][row] = tfno



# ========================================================================================================
# GOAL: minimize the number of pilots needed
# In this case, all TFs should be supported.
# Due to the start time and end time constraints, we still sort all TFs and do scheduling one by one.
# When sorting, 1) flexibility: payload/transmission period  2) payload

# Basic scheduling policy: height lower & right justified
# ========================================================================================================

# Sorting traffic flows according to flexibility & payload
def sortTFs(tflist):
    # Step1: ratio: payload/transmission period
    # Step2: payload
    list1 = sorted(tflist, key=lambda x: (x.initial_time, -x.payload))
    return list1


TFlist = sortTFs(TFlist)


# [CORE FUNCTION] generate scheduling plan: return true or false, if true, also output the scheduling info
# two return value: 1) true or false   2) scheduling info
def generateschedule(pilots):
    # new instance of a resource grid
    rg = ResourceGrid(numberofslots, pilots)

    for tf in TFlist:
        # tf_start_time = datetime.now()
        # Step1: generate all scheduling intervals using offset and transmission period
        schedulingintervals = [[math.ceil(tf.initial_time + tf.transmission_period * i),
                                math.floor(tf.initial_time + tf.transmission_period * i + tf.delay_requirement - 1)]
                               for i in range(math.floor(numberofslots / tf.transmission_period))]
        tf.scheduling_interval = schedulingintervals

        if tf.naivescheduling(rg) == -1:
            print('No solution, fail! %d' % pilots)
            return -1

    print('Find Solution! %d' % pilots)
    print('resource grid after assignment:')
    print('=' * 20, file=log)
    top_list = []
    usedru = 0
    tmp_ru_ss = ''
    # for rowindex in range(pilots - 1, -1, -1):
    for rowindex in range(pilots):
        ss = ''
        row_ru = 0
        for colindex in range(0, numberofslots):
            if rg.data[colindex][rowindex] == -1:
                ss += '0 '
            else:
                # ss += '%c ' % (rg.data[colindex][rowindex] + ord('A'))
                ss += '1 '
                # resource unit for data
                if rg.data[colindex][rowindex] < interval_data_control:
                    usedru += 1
                    row_ru += 1
                top_list.append(rowindex + 1)
        tmp_ru_ss += ' %f' % (row_ru / hyper_period)
        # print(ss)
        print(ss, file=log)
    print(tmp_ru_ss, file=log_heatmap)
    max_pilot = max(top_list)
    print('Max pilot: %d' % max_pilot)
    # output resource efficiency
    efficiency = usedru / (numberofslots * max_pilot)
    # number of packets
    numberofpackets = 0
    allowedconfigurations = 0
    actualconfigurations = 0
    for tf in TFlist:
        numberofpackets += int(hyper_period / tf.transmission_period)
        allowedconfigurations += tf.numberofconfigurations
        actualconfigurations += tf.numberofconfigurations_actual

    return max_pilot, efficiency, numberofpackets


minimumpilots, efficiency, numberofpackets = generateschedule(nopilots)
solvingtime = datetime.now() - timeSystemStart
solvingtime = solvingtime.total_seconds()*1000
# print('\n Max pilots: %d' % minimumpilots)
print('%s %d' % (solvingtime, numberofpackets), file=log_solvingtime)
print('%d %f' % (minimumpilots, efficiency), file=log_pilots)
