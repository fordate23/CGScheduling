import numpy as np
import math
import sys

sys.path.append('../DataGeneration')
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
# confname = ['COmax', '50', '20', '15','10', '5', '2', '1']
# confname = [1, 0.8, 0.6, 0.4, 0.2, 0.1, 0.01, 0]
confname = ['COmax', '1']
folder_name = ['10', '20', '30', '40', '50', '60', '70', '80']

# distance between offset
distance_control_payload = 50

# symbol used to separate control and data
interval_data_control = 1000

# constraints on number of available offset attempts
number_of_offset_attempts = 5

timeSystemStart = datetime.now()

# This aims to implement a basic prototype for solving the resource scheduling problem.

# First Step: define traffic flow: 0 initial time 1 transmission period   2 payload   3 latency

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))
arguments = sys.argv

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
# foldername
whichfolder = int(arguments[6])

# log = open('../Heuristic/results/%d.txt' % noseries, 'w')
# log_solvingtime = open('../Heuristic/%d/solvingtime_%s.txt' % (int(folder_name[whichfolder]), confname[noconfname]), 'a')
# log_pilots = open('../Heuristic/%d/pilots_%s.txt' % (int(folder_name[whichfolder]), confname[noconfname]), 'a')
log = open('../Heuristic/%s/results/%d.txt' % (confname[noconfname], noseries), 'w')
log_solvingtime = open('../Heuristic/%s/solvingtime_%s.txt' % (confname[noconfname], int(folder_name[whichfolder])), 'a')
log_pilots = open('../Heuristic/%s/pilots_%s.txt' % (confname[noconfname], int(folder_name[whichfolder])), 'a')
log_heatmap = open('../Heuristic/%s/heatmap_%s.txt' % (confname[noconfname], int(folder_name[whichfolder])), 'a')


class TF:
    # list of functions
    def __init__(self, initial_time, transmission_period, payload, delay_req, numberofconf, con_overhead, number):
        self.initial_time = initial_time
        self.transmission_period = transmission_period
        self.payload = payload
        self.delay_requirement = delay_req
        self.numberofconfigurations = numberofconf  # max configurations (BS)
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
        square_max = min(self.payload + allowedAdditionalRB, int(math.pow(math.ceil(math.sqrt(self.payload)), 2)))
        for target_payload in range(self.payload, square_max + 1):
            for width in range(1, int(self.delay_requirement) + 1):
                if target_payload % width == 0:
                    self.shapelist.append([width, int(target_payload / width)])
        # print('payload: %d' % self.payload)
        # print('Shape list:')
        # print(self.shapelist)

    def set_scheduling_info(self, scheduling_info):
        self.scheduling_info.append(scheduling_info)

    def set_tmp_scheduling_info(self, scheduling_info):
        self.tmp_scheduling_info.append(scheduling_info)

    # for matching the maximum number of configurations
    def mactch_max_configurations(self, rg):
        number_of_packets = int(hyper_period / self.transmission_period)
        # define the search space
        offset_min = self.scheduling_interval[0][0]

        min_height = 999999
        min_new_scheduling_info = []
        for shape_alternative in range(len(self.shapelist)):
            offset_max = self.scheduling_interval[0][1] - self.shapelist[shape_alternative][0] + 1
            if offset_max < offset_min:
                continue
            # decide offset, the number is constrained by 'number_of_offset_attempts'
            # offsets = []
            # if offset_max <= number_of_offset_attempts:
            #     for tmp_offset in range(offset_min, offset_max + 1):
            #         offsets.append(tmp_offset)
            # else:
            #     step = (offset_max-offset_min) / number_of_offset_attempts
            #     for tmp_offset in range(number_of_offset_attempts):
            #         offsets.append(int(offset_min + tmp_offset * step))
            # print('offsets')
            # print(offsets)
            for tmp_offset in range(offset_min, offset_max + 1):
            # for tmp_offset in offsets:
                offset_ = tmp_offset

                tp_ = self.transmission_period
                width_ = self.shapelist[shape_alternative][0]
                height_ = self.shapelist[shape_alternative][1]
                bottom_ = self.tmp_scheduling_info[0][2]
                current_height = bottom_ + height_

                # generate all scheduling info for each data packet
                new_scheduling_info = []
                # element format: [l, r, b, h]
                for packets in range(number_of_packets):
                    # for each packet
                    new_scheduling_info.append([int(offset_ + tp_ * packets),
                                                int(offset_ + tp_ * packets + width_ - 1),
                                                int(bottom_),
                                                int(height_)])
                # print('New scheduling info:')
                # print(new_scheduling_info)

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

                        # for col in range(left, right + 1):
                        #     for row in range(bottom, bottom + height):
                        #         if rg.data[col][row] != -1:
                        #             # print('collision!')
                        #             success_flag = False
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
                            current_height += 1

                # after searching all
                if current_height < min_height:
                    min_new_scheduling_info = new_scheduling_info
                    min_height = current_height

        # print('Min new scheduling info:')
        # print(min_new_scheduling_info)
        # Update resource grid
        for packet_info_index in range(len(min_new_scheduling_info)):
            self.scheduling_info.append(min_new_scheduling_info[packet_info_index])

            left = min_new_scheduling_info[packet_info_index][0]
            right = min_new_scheduling_info[packet_info_index][1]
            bottom = min_new_scheduling_info[packet_info_index][2]
            height = min_new_scheduling_info[packet_info_index][3]

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

    # other possible functionalities
    # Function1: list all stairs
    # [start_index, end_index, distance to top]
    def liststairs(self, s, e):
        stair = False  # at beginning, stair status is false
        stair_top = -1
        stairlist = []
        stair_end = -1
        stair_start = -1
        if s == e:
            for frequency_pointer in range(self.pilots - 1, -1, -1):
                # print(self.data[time_pointer][frequency_pointer])
                if self.data[s][frequency_pointer] != -1:
                    stair_top = frequency_pointer
                    break
                else:
                    if frequency_pointer == 0:
                        stair_top = -1
            stairlist.append([s, s, self.pilots - 1 - stair_top])
        else:
            for time_pointer in range(e, s - 1, -1):
                # check stair status
                if not stair:
                    # if there is no stair, then find one
                    for frequency_pointer in range(self.pilots - 1, -1, -1):

                        if self.data[time_pointer][frequency_pointer] != -1:
                            stair = True
                            stair_top = frequency_pointer
                            stair_end = stair_start = time_pointer
                            break
                        else:
                            if frequency_pointer == 0:
                                stair = True
                                stair_top = -1
                                stair_end = stair_start = time_pointer
                else:
                    # if there is stair, record the old top and find the next top, and compare
                    old_stair_top = stair_top
                    for frequency_pointer in range(self.pilots - 1, -1, -1):
                        if self.data[time_pointer][frequency_pointer] != -1:
                            stair = True
                            stair_top = frequency_pointer
                            break
                        else:
                            if frequency_pointer == 0:
                                stair = True
                                stair_top = -1

                    # now, find a new top
                    if old_stair_top == stair_top:
                        # keep searching
                        stair_start = time_pointer
                        # probably close to the boundary
                        if time_pointer == s:
                            stairlist.append([s, stair_end, self.pilots - 1 - stair_top])
                    else:
                        # not equal
                        stairlist.append([stair_start, stair_end, self.pilots - 1 - old_stair_top])
                        stair_end = stair_start = time_pointer
                        if time_pointer == s:
                            stairlist.append([s, stair_end, self.pilots - 1 - stair_top])
        # for each stair, calculate the free space
        new_stairlist = []
        for ele in stairlist:
            old_start = ele[0]
            old_end = ele[1]
            current_distance = ele[2]
            if current_distance == 0:
                continue
            new_start = old_start
            new_end = old_end
            pointer_distance = -1
            # for the end
            if old_end == e:
                new_end = e
            else:
                for pointer in range(old_end + 1, e + 1):
                    for checkele in stairlist:
                        if checkele[0] <= pointer <= checkele[1]:
                            pointer_distance = checkele[2]
                    if pointer_distance >= current_distance:
                        new_end = pointer
                    else:
                        new_end = pointer - 1
                        break

            # for the start
            if old_start == s:
                new_start = s
            else:
                for pointer in range(old_start - 1, s - 1, -1):
                    for checkele in stairlist:
                        if checkele[0] <= pointer <= checkele[1]:
                            pointer_distance = checkele[2]
                    if pointer_distance >= current_distance:
                        new_start = pointer
                    else:
                        new_start = pointer + 1
                        break
            new_stairlist.append([ele[0], ele[1], ele[2], new_start, new_end])
        return new_stairlist


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
    list1 = sorted(tflist, key=lambda x: (x.ratiopayloadtransmissionperid, x.payload), reverse=True)
    return list1


TFlist = sortTFs(TFlist)


# [CORE FUNCTION] generate scheduling plan: return true or false, if true, also output the scheduling info
# two return value: 1) true or false   2) scheduling info
def generateschedule(pilots):
    # new instance of a resource grid
    rg = ResourceGrid(numberofslots, pilots)

    for tf in TFlist:
        schedulingintervals = [[math.ceil(tf.initial_time + tf.transmission_period * i),
                                math.floor(tf.initial_time + tf.transmission_period * i + tf.delay_requirement - 1)]
                               for i in range(math.floor(numberofslots / tf.transmission_period))]
        tf.scheduling_interval = schedulingintervals
        # print(tf)
        # print(schedulingintervals)
        # print(tf)
        # print('shape_list')
        # print(tf.shapelist)
        # for each data packet, find the optimal position
        intervals = schedulingintervals[0]
        # 1) find stairs from the right side, using function from rg, return a list
        # print('interval liststair: %d %d %d' % (tf.number, intervals[0], intervals[1]))
        # print('offset: %d  tp: %d  delay: %d' % (tf.initial_time, tf.transmission_period, tf.delay_requirement))
        stairlist = rg.liststairs(intervals[0], intervals[1])
        # 2) sort stairs, first distance, second close to the deadline
        stairlist = sorted(stairlist, key=lambda x: (x[2], x[0]), reverse=True)

        # format: [left, right, bottom, height, final_height]
        lowest_for_eachstair = []
        for eachstair in stairlist:
            # stair: 0 stair_start  1 stair_end  2 stair distance  3 flat start  4 flat end
            # 3) find the most "lowest" shape for the current stairs
            # 3.1) get the free space for each stair
            freespace = eachstair[4] - eachstair[3] + 1
            # find the lowest height for all shapes
            min_height = 999999
            right_min = 0
            left_min = 0
            bottom_min = 0
            height_min = 0
            for alternative in range(len(tf.shapelist)):
                # width and height can hold
                if tf.shapelist[alternative][0] <= freespace and tf.shapelist[alternative][1] <= eachstair[2]:
                    # calculate the position of alternatives
                    right = eachstair[4]
                    left = right - tf.shapelist[alternative][0] + 1
                    bottom = pilots - eachstair[2]
                    height = tf.shapelist[alternative][1]
                    final_height = bottom + height
                    # compare with the current minimum one
                    if final_height < min_height:
                        min_height = final_height
                        right_min = right
                        left_min = left
                        bottom_min = bottom
                        height_min = height
            # after iterating all shapes, record the minimal one
            lowest_for_eachstair.append([left_min, right_min, bottom_min, height_min, min_height])
        # after having all min info for each stair,
        # select the minimal one with the right position
        # select the rightest one with minimal width to avoid resource wastage
        lowest_for_eachstair = sorted(lowest_for_eachstair, key=lambda x: (x[4], -x[1], (x[1] - x[0])))
        # print('After having all lowest...')
        # print(lowest_for_eachstair)

        # After having the sub-optimal

        tf.set_tmp_scheduling_info([lowest_for_eachstair[0][0],
                                    lowest_for_eachstair[0][1],
                                    lowest_for_eachstair[0][2],
                                    lowest_for_eachstair[0][3]])

        if tf.mactch_max_configurations(rg) == -1:
            print('No solution, fail! %d' % pilots)
            return -1

    print('Find Solution! %d' % pilots)
    print('resource grid after assignment:')
    print('=' * 20, file=log)
    top_list = []
    usedru = 0
    tmp_ru_ss = ''
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

    for tf in TFlist:
        numberofpackets += int(hyper_period / tf.transmission_period)


    return max_pilot, efficiency, numberofpackets


minimumpilots, efficiency, numberofpackets = generateschedule(nopilots)
solvingtime = datetime.now() - timeSystemStart
solvingtime = solvingtime.total_seconds()*1000
# print('\n Max pilots: %d' % minimumpilots)
print('%s %d' % (solvingtime, numberofpackets), file=log_solvingtime)
print('%d %f' % (minimumpilots, efficiency), file=log_pilots)
