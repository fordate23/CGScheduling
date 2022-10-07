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
        # print(self.tmp_scheduling_info)
        # preprocessing for tmp configurations
        # STEP A: calculate the number of actual configurations..
        # Step A.1: get shape and interval of all rectangles
        width = []
        height = []
        bottom = []
        interval = [0]
        for ele in self.tmp_scheduling_info:
            width.append(ele[1] - ele[0] + 1)
            bottom.append(ele[2])
            height.append(ele[3])
        for i in range(len(self.tmp_scheduling_info) - 1):
            interval.append(self.tmp_scheduling_info[i + 1][0] - self.tmp_scheduling_info[i][0])

        # print(self.tmp_scheduling_info)
        # print('-' * 20)
        # print(width)
        # print(bottom)
        # print(height)
        # print(interval)

        # flags for configuration for each data packet
        flag_conf = [False] * len(width)

        # Step A.2: first check periodicity
        previous_periodicity = -1
        for ele in range(len(interval)):
            if not previous_periodicity == interval[ele]:
                flag_conf[ele] = True
                if ele == len(interval) - 1:
                    break
                previous_periodicity = interval[ele + 1]

        # Step A.3: then check each shape
        current_shape = [-1, -1, -1]
        for ele in range(len(width)):
            if not (width[ele] == current_shape[0] and bottom[ele] == current_shape[1] and height[ele] == current_shape[
                2]):
                flag_conf[ele] = True
            current_shape[0] = width[ele]
            current_shape[1] = bottom[ele]
            current_shape[2] = height[ele]

        # print(flag_conf)

        # Step A.4: calculate number of configurations (actual)
        config_count = 0
        for ele in flag_conf:
            if ele:
                config_count += 1
        # print('Actual configurations: %d \n' % config_count)

        # Step A.5: check number of maximum configuration
        if config_count <= self.numberofconfigurations:
            # print('Initial scheduling info <= maximum number of configurations.')
            # update resource gird
            # check: resource collision with current resource grid
            while True:
                success_flag = True
                for packet_info_index in range(len(self.tmp_scheduling_info)):
                    left = self.tmp_scheduling_info[packet_info_index][0]
                    right = self.tmp_scheduling_info[packet_info_index][1]
                    bottom = self.tmp_scheduling_info[packet_info_index][2]
                    height = self.tmp_scheduling_info[packet_info_index][3]
                    # check max pilot constraint for avoiding out of bound
                    if bottom + height > nopilots:
                        print('No solution, fail!   2')
                        return -1

                    for col in range(left, right + 1):
                        for row in range(bottom, bottom + height):
                            if rg.data[col][row] != -1:
                                # print('collision!')
                                success_flag = False
                if success_flag:
                    break
                else:
                    # update scheduling info: increment 'bottom' by 1
                    for ele in self.tmp_scheduling_info:
                        ele[2] += 1

            # Update resource grid
            for packet_info_index in range(len(self.tmp_scheduling_info)):
                self.scheduling_info.append(self.tmp_scheduling_info[packet_info_index])
                left = self.tmp_scheduling_info[packet_info_index][0]
                right = self.tmp_scheduling_info[packet_info_index][1]
                bottom = self.tmp_scheduling_info[packet_info_index][2]
                height = self.tmp_scheduling_info[packet_info_index][3]

                for col in range(left, right + 1):
                    for row in range(bottom, bottom + height):
                        rg.data[col][row] = self.number

            return

        # If not, then Step B
        # print('Initial scheduling info: %d \n maximum conf. : %d' % (config_count, self.numberofconfigurations))
        # Since edge packet and middle packet own different influence on no. configuration
        # all cases need to be listed, OR just use a specified policy

        # Policy: evenly distribute the data packets across configurations
        # Step B.1 calculate the size of current configurations
        # print('Current conf. status: ')
        # print(flag_conf)
        # Having a list for storing this info
        # format: [index of conf., size (contained packets)]
        config_series = []
        current_conf_size = 0
        for flag_index in range(len(flag_conf)):
            # at the beginning, 'new_start_flag' is 1
            if flag_conf[flag_index]:
                # for the middle conf.
                if flag_index != 0:
                    config_series.append([flag_index - current_conf_size, current_conf_size])
                # ........T     the last packet is T
                if flag_index == len(flag_conf) - 1:
                    config_series.append([flag_index, 1])
                    break
                current_conf_size = 1
            else:
                current_conf_size += 1
                # ......TFF     the last one is F
                if flag_index == len(flag_conf) - 1:
                    config_series.append([flag_index - current_conf_size + 1, current_conf_size])
        # print('Current conf. series:')
        # print(config_series)

        # Step B.2      combine several conf. together: finally, number of segments == self.numberofconfigurations
        # Step B.2.1    calculate the needed size of each segment
        segment_size = sum([ele[1] for ele in config_series]) / self.numberofconfigurations
        # Step B.2.2    iterate all conf. and combine some of them according to the size of each segment
        # create a list to store the result, here use the name 'new_configuration_list'
        # format: [index of configuration, number of impacted data packets]
        new_configuration_list = []
        tmp_sum = 0
        start_index = 0
        for config_index in range(len(config_series)):
            tmp_sum += config_series[config_index][1]
            # till the end
            if config_index == len(config_series) - 1:
                new_configuration_list.append([config_series[start_index][0], tmp_sum])
                break
            if tmp_sum > segment_size:
                new_configuration_list.append([config_series[start_index][0], tmp_sum])
                tmp_sum = 0
                start_index = config_index + 1
        # print('New configuration list:')
        # print(new_configuration_list)

        # # Step B.1 for all current conf.   collect the top
        # # format: [index of conf., top]
        # top_list = []
        # for ele in range(len(self.tmp_scheduling_info)):
        #     if flag_conf[ele]:
        #         top_list.append([ele, self.tmp_scheduling_info[ele][2] + self.tmp_scheduling_info[ele][3]])
        # # print('Top list of current configurations:')
        # # print(top_list)
        # top_list = sorted(top_list, key=lambda x: (x[1], x[0]), reverse=True)
        # # top_list = sorted(top_list, key=lambda x: x[0]) --- Interesting....
        # # print('Top list after sorting...')
        # # print(top_list)
        #
        # # each item corresponding to one newly generated configuration
        # new_configuration_list = []
        # # format of each element
        # # [index of configuration, number of impacted data packets]
        # # Step B.2  select all
        # # follow first conf.
        # if self.numberofconfigurations == 1:
        #     # only one conf.  the impacted range is 0 through 'all packets'
        #     new_configuration_list.append([0, len(flag_conf)])
        # else:
        #     # for multiple conf.
        #     # Use first proposal: select [no. conf. - 1] conf. with highest top
        #     # T___T___T___  e.g. no. conf. = 3  select 2 conf.
        #     number_of_select_conf = self.numberofconfigurations - 1
        #     # get index of 'highest top'
        #     select_conf_index = top_list[:number_of_select_conf]
        #     select_conf_index = sorted(select_conf_index, key=lambda x: x[0])
        #     # print('Selected index of conf and top:')
        #     # print(select_conf_index)
        #
        #     # generate new configuration element
        #     # check: first ele is start
        #     # if select_conf_index[0][0] == 0:
        #     #     # select the start conf.
        #     #     new_configuration_list.append([0, select_conf_index[1][0] - 1])
        #     # # check: last ele is end
        #     # if select_conf_index[-1][0] == numberofslots - 1:
        #     #     new_configuration_list.append([numberofslots - 1, 1])
        #     for index in range(number_of_select_conf):
        #         if index == 0:
        #             new_configuration_list.append([0, select_conf_index[0][0] - 0])
        #         if index == number_of_select_conf - 1:
        #             new_configuration_list.append([select_conf_index[index][0],
        #                                            len(flag_conf) - select_conf_index[index][0]])
        #             break
        #
        #         new_configuration_list.append([select_conf_index[index][0],
        #                                        (select_conf_index[index + 1][0] - select_conf_index[index][0])])
        #
        #     # print('New configuration list:')
        #     # print(new_configuration_list)

        # Step B.3: generate scheduling info for each item in 'new_configuration_list'
        # format of each element
        # [index of configuration, number of impacted data packets]
        for index in range(len(new_configuration_list)):
            # for each configuration, calculate [offset, periodicity, width, height, bottom]
            # OPTIMIZATION here to generate new configuration information

            start_conf_index = new_configuration_list[index][0]
            number_of_packets = new_configuration_list[index][1]
            if number_of_packets == 0:
                continue
            # define the search space
            offset_min = self.scheduling_interval[start_conf_index][0]

            min_height = 999999
            min_new_scheduling_info = []
            for shape_alternative in range(len(self.shapelist)):
                offset_max = self.scheduling_interval[start_conf_index][1] - self.shapelist[shape_alternative][0] + 1
                if offset_max < offset_min:
                    continue
                # decide offset, the number is constrained by 'number_of_offset_attempts'
                offsets = []
                if offset_max <= number_of_offset_attempts:
                    for tmp_offset in range(offset_min, offset_max + 1):
                        offsets.append(tmp_offset)
                else:
                    step = (offset_max-offset_min) / number_of_offset_attempts
                    for tmp_offset in range(number_of_offset_attempts):
                        offsets.append(int(offset_min + tmp_offset * step))
                # print('offsets')
                # print(offsets)
                # for tmp_offset in range(offset_min, offset_max + 1):
                for tmp_offset in offsets:
                    offset_ = tmp_offset

                    tp_ = self.transmission_period
                    width_ = self.shapelist[shape_alternative][0]
                    height_ = self.shapelist[shape_alternative][1]
                    bottom_ = self.tmp_scheduling_info[start_conf_index][2]
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

    # for control, analyze all scheduling info to investigate how many configurations
    # and the offset of each configuration
    def analyze_scheduling_info(self):
        # Step 1: get shape and interval of all rectangles
        width = []
        height = []
        bottom = []
        interval = [0]
        # print('..... scheduling info...')
        # print(self.scheduling_info)
        for ele in self.scheduling_info:
            width.append(ele[1] - ele[0] + 1)
            bottom.append(ele[2])
            height.append(ele[3])
        for i in range(len(self.scheduling_info) - 1):
            interval.append(self.scheduling_info[i + 1][0] - self.scheduling_info[i][0])

        # print('Width:......')
        # print(width)
        # print(bottom)
        # print(height)
        # print(interval)

        # flags for configuration for each data packet
        flag_conf = [False] * len(width)

        # Step 2: first check periodicity
        previous_periodicity = -1
        for ele in range(len(interval)):
            if not previous_periodicity == interval[ele]:
                flag_conf[ele] = True
                if ele == len(interval) - 1:
                    break
                previous_periodicity = interval[ele + 1]

        # Step 3: then check each shape
        current_shape = [-1, -1, -1]
        for ele in range(len(width)):
            if not (width[ele] == current_shape[0] and bottom[ele] == current_shape[1] and height[ele] == current_shape[
                2]):
                flag_conf[ele] = True
            current_shape[0] = width[ele]
            current_shape[1] = bottom[ele]
            current_shape[2] = height[ele]

        # print(flag_conf)

        # Step 4: calculate number of configurations (actual)
        count = 0
        for ele in flag_conf:
            if ele:
                count += 1
        self.numberofconfigurations_actual = count
        # print('Actual configurations: %d \n' % self.numberofconfigurations_actual)

        # Step 5: get offset for each configuration (actual)
        for ele in range(len(flag_conf)):
            if flag_conf[ele]:
                self.offset_configurations_actual.append(self.scheduling_info[ele][0])
        # print('Offset for each configurations: ')
        # print(self.offset_configurations_actual)
        # print('\n')


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
        # tf_start_time = datetime.now()
        # Step1: generate all scheduling intervals using offset and transmission period
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
        for intervals in schedulingintervals:
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
        # first_scheduling_finished_time = datetime.now()
        # print('Initial Scheduling finished: %s' % (first_scheduling_finished_time - tf_start_time))
        # print('Scheduling intervals:')
        # print(schedulingintervals)
        # print('Tmp scheduling info:')
        # print(tf.tmp_scheduling_info)
        # print('TF info:')
        # print('%d %d %d' % (tf.initial_time, tf.transmission_period, tf.delay_requirement))
        if tf.mactch_max_configurations(rg) == -1:
            print('No solution, fail! %d' % pilots)
            return -1
        # after_match_max_configuration_time = datetime.now()
        # print('Atfer match max configuration: %s' % (after_match_max_configuration_time
        #                                              - first_scheduling_finished_time))
        # after data transmission, check configurations, then allocate resource for control messages
        # print('Analyse data-configurations...')
        # print(tf.scheduling_info)
    for tf in TFlist:
        tf.analyze_scheduling_info()
        # print('After match_max... the real actual configuration: %d' % tf.numberofconfigurations_actual)
        analyze_scheduling_info_time = datetime.now()
        # print('Analyze scheduling info: %s' % (analyze_scheduling_info_time - after_match_max_configuration_time))
        # for control: allocate resource for each control message
        width_control = tf.control_message_width
        height_control = tf.control_message_height

        # number of needed control message
        number_needed_control_message = tf.numberofconfigurations_actual - 1
        if number_needed_control_message == 0:
            # print('No need to have explict control message')
            continue
        # print('offset configuration actual:')
        # print(tf.offset_configurations_actual)
        # print('scheduling info')
        # print(tf.scheduling_info)
        control_schedule_interval = [[0,
                                      tf.offset_configurations_actual[i] - 1]
                                     for i in range(1, tf.numberofconfigurations_actual)]
        # To speedup the 'list stair' process
        # have an status map for the current resource grid
        # tmp_rg_top = []
        # for check_index in range(0, numberofslots):
        #     stair_top = -1
        #     for frequency_pointer in range(nopilots - 1, -1, -1):
        #         # print(self.data[time_pointer][frequency_pointer])
        #         if rg.data[check_index][frequency_pointer] != -1:
        #             stair_top = frequency_pointer
        #             break
        #         else:
        #             if frequency_pointer == 0:
        #                 stair_top = -1
        #     tmp_rg_top.append([check_index, stair_top + 1])
        # print('Before control message, the resource grid:')
        # for rowindex in range(pilots - 1, -1, -1):
        #     ss = ''
        #     for colindex in range(0, numberofslots):
        #         if rg.data[colindex][rowindex] == -1:
        #             ss += '0 '
        #         else:
        #             ss += '%c ' % (rg.data[colindex][rowindex] + ord('A'))
        #     print(ss)
        # print('Top for all columns:')
        # print(tmp_rg_top)

        for intervals_control in range(len(control_schedule_interval)):

            start_index = control_schedule_interval[intervals_control][0]
            end_index = control_schedule_interval[intervals_control][1]
            # print('Start Index: %d  end index: %d' % (start_index, end_index))
            if end_index - start_index > distance_control_payload:
                start_index = end_index - distance_control_payload
            # search for all available for control messages
            # format: [colindex, bottom, height]
            free_space_list = []
            for check_index in range(start_index, end_index + 1):
                # stair_top = -1
                start_frequency_pointer = nopilots - 1
                # at the very beginning, we have the free space
                con_flag = 1
                for frequency_pointer in range(nopilots - 1, -1, -1):
                    # print(self.data[time_pointer][frequency_pointer])
                    if rg.data[check_index][frequency_pointer] != -1 and con_flag:
                        h = start_frequency_pointer - frequency_pointer
                        if h >= tf.control_message_height:
                            free_space_list.append([check_index, frequency_pointer + 1, h])
                        con_flag = 0
                    elif frequency_pointer == 0 and con_flag:
                        h = start_frequency_pointer - frequency_pointer + 1
                        if h >= tf.control_message_height:
                            free_space_list.append([check_index, frequency_pointer, h])
                    # keep searching for free space
                    if rg.data[check_index][frequency_pointer] == -1 and (not con_flag):
                        start_frequency_pointer = frequency_pointer
                        con_flag = True
            # print('Free space list:')
            # print(free_space_list)
            # try:
            #     select_index = sorted(free_space_list,
            #                           key=lambda x: (x[1], x[2], -x[0]))[0]
            # except:
            #     print(tf)
            #     print(free_space_list)
            #     print('scheduling intervals')
            #     print(tf.scheduling_interval)
            #     print('tmp scheduling info')
            #     print(tf.tmp_scheduling_info)
            #     print('scheduling info')
            #     print(tf.scheduling_info)
            #     print('offset of actual scheduling info')
            #     print(tf.offset_configurations_actual)
            #     print('generated control scheduling interval')
            #     print(control_schedule_interval)
            # print(select_index)
            # print('after:')
            # print(top_list)

            select_index = sorted(free_space_list,
                                  key=lambda x: (x[1], x[2], -x[0]))[0]
            lowest_col = select_index[0]
            if select_index[1] + height_control >= nopilots:
                return -1
            else:
                rg.update(lowest_col, lowest_col, select_index[1], height_control, tf.number + interval_data_control)
                # update tmp_rg_top
                # tmp_rg_top[lowest_col][1] += height_control

        after_control_message_time = datetime.now()
        print('After control message: %s' % (after_control_message_time - analyze_scheduling_info_time))

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

    return max_pilot, efficiency, numberofpackets, allowedconfigurations, actualconfigurations


minimumpilots, efficiency, numberofpackets, maxconf, actualconf = generateschedule(nopilots)
solvingtime = datetime.now() - timeSystemStart
solvingtime = solvingtime.total_seconds()*1000
# print('\n Max pilots: %d' % minimumpilots)
print('%s %d' % (solvingtime, numberofpackets), file=log_solvingtime)
print('%d %f %d %d' % (minimumpilots, efficiency, maxconf, actualconf), file=log_pilots)
