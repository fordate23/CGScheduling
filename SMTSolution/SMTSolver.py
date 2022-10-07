from z3 import *
import math
from datetime import datetime
from TF import *
import sys
import numpy as np

sys.path.append('../DataGeneration/')
# from DataGeneration.application_parameter import hyper_period
from DataGeneration.network_parameter import length_timeslot

timeSystemStart = datetime.now()
log_solvingtime = open('../SMTSolution/solvingtime.txt', 'a')
log_pilots = open('../SMTSolution/results.txt', 'a')
SoF = True

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))
arguments = sys.argv
# arguments = ['..\\SMTSolution\\SMTSolver_optimized.py', '33', '3', '4', '2',
#              '0', '5', '4', '3', '1',
#              '0', '5', '2', '3', '1',
#              '0', '2', '1', '2', '3']

# arguments = ['..\\SMTSolution\\SMTSolver_optimized.py', '33', '2', '5', '10',
#              '0', '5', '2', '3', '2', '1',
#              '0', '2', '2', '2', '2', '1']

# arguments = ['..\\SMTSolution\\SMTSolver_optimized.py', '33', '1', '4', '2',
#              '0', '5', '1', '2', '2']

# 'Theoreticalbound.py', '7 4 6 20  ' \
#                        '1.000000 20.000000 14.000000 12.000000 1.000000 1.000000 ' \
#                        '3.000000 20.000000 4.000000 12.000000 1.000000 1.000000 ' \
#                        '1.000000 4.000000 2.000000 2.000000 5.000000 1.000000 ' \
#                        '6.000000 20.000000 4.000000 12.000000 1.000000 1.000000


# arguments = ['~', '33', '4', '6', '20',
#              '1', '20', '14', '12', '1', '1',
#              '3', '20', '4', '12', '1', '1',
#              '1', '4', '2', '2', '5', '1',
#              '6', '20', '4', '12', '1', '1']

# python Theoreticalbound.py 35 4 6 20
# 4.000000 20.000000 7.000000 12.000000 1.000000 1.000000
# 0.000000 4.000000 8.000000 2.000000 5.000000 1.000000
# 0.000000 4.000000 1.000000 2.000000 5.000000 1.000000
# 0.000000 4.000000 2.000000 2.000000 5.000000 1.000000'

# arguments = ['~', '35', '4', '6', '20',
#              '4', '20', '7', '12', '1', '1',
#              '0', '4', '8', '2', '5', '1',
#              '0', '4', '1', '2', '5', '1',
#              '0', '4', '2', '2', '5', '1']

# ==================================== Read settings from invoke.py =======================
# nrof Series
noseries = int(arguments[1])
# INPUT: the information for traffic flows
number_of_TrafficFlows = int(arguments[2])
# no. of the current configs in the series
nopilots = int(arguments[3])
# hyper-period
hyper_period = int(arguments[4])

# collection of all traffic flows
list_of_TrafficFlows = []
# fill in the above list using the parameters from 'arguments'
# number of attributes
number_attributes = 6
# reading offset
reading_offset = 4
for i in range(number_of_TrafficFlows):
    initial_time_ = float(arguments[i * number_attributes + reading_offset + 1])
    transmission_period_ = float(arguments[i * number_attributes + reading_offset + 2])
    payload_ = int(float(arguments[i * number_attributes + reading_offset + 3]))
    latency_ = float(arguments[i * number_attributes + reading_offset + 4])
    numberofconf = int(float(arguments[i * number_attributes + reading_offset + 5]))
    control_overhead = int(float(arguments[i * number_attributes + reading_offset + 6]))

    print('%f %f %d %f %d %d' %
          (initial_time_, transmission_period_, payload_, latency_, numberofconf, control_overhead))
    list_of_TrafficFlows.append(TF(initial_time=initial_time_,
                                   transmission_period=transmission_period_,
                                   payload=payload_,
                                   delay_req=latency_,
                                   numberofconf=numberofconf,
                                   control_o=control_overhead))
assert len(list_of_TrafficFlows) == number_of_TrafficFlows

# record the current time, used to calculate the time elapsed in each stage
time_SystemStart = datetime.now()

# Start recording the status of the overall program
log_file = open('../SMTSolution/results/%d.txt' % noseries, 'w')
log_file_ = open('../SMTSolution/results/%d_Report.txt' % noseries, 'w')

# maximum allowed configurations
sum_maximum_conf = sum([tf.numberofconfigurations for tf in list_of_TrafficFlows])


ss = 'Start Time: %s\n' % time_SystemStart
print(ss)
log_file.write(ss)

verbose = True  # print information
log = True  # output text information to the log file

# LOG: information of traffic flows
if log:
    log_file.write('=' * 20 + 'INFORMATION OF TRAFFIC FLOWS' + '=' * 20 + '\n')
    for i in range(len(list_of_TrafficFlows)):
        s = 'Index: %d \t ' \
            'Initial Offset: %f \t' \
            'Transmission Period: %f \t' \
            'Payload: %d resource units \t' \
            'Maximum Delay Requirement: %f \t' \
            'Maximum number of configurations: %d \t' \
            'Control overhead: %d resource units \n' % (i,
                                                        list_of_TrafficFlows[i].initial_time,
                                                        list_of_TrafficFlows[i].transmission_period,
                                                        list_of_TrafficFlows[i].payload,
                                                        list_of_TrafficFlows[i].delay_requirement,
                                                        list_of_TrafficFlows[i].numberofconfigurations,
                                                        list_of_TrafficFlows[i].control_overhead)
        log_file.write(s)

log_file.write('=' * 20 + 'SYSTEM PARAMETERS' + '=' * 20 + '\n')
# TODO：the accuracy of each transmission period = 0.1
# transmissionperiodlist = [int(i.transmission_period) for i in list_of_TrafficFlows]
# hyper_Period = np.lcm.reduce(transmissionperiodlist)
hyper_Period = hyper_period
log_file.write('Length of each time slot: %f \n' % length_timeslot)
log_file.write('Hyper-period: %f \n' % hyper_Period)
# log_file.write('Resource units for control overhead: %d \n' % rbs_control)

# Acquire the number of pilots and then generate the 'resource block allocation scheme'
# For example, if the pilots = 3, then all possible allocation schemes are as following:
# 1 0 0 1 0 1
# 0 1 0 1 1 1
# 0 0 1 0 1 1
# there are 6 columns which means that for each data packet, the possible resource allocation scheme has 6 options
number_of_Pilots = nopilots
print('number of pilots: %d' % nopilots)
max_RBAllocationPatterns = int((number_of_Pilots * (number_of_Pilots + 1)) / 2)
frequency_Pattern = []

# record the index of top RB as the auxiliary function for the optimization goal
frequency_Pattern_top = []
for i in range(number_of_Pilots):
    for s in range(0, number_of_Pilots - i):
        frequency_Pattern_top.append(nopilots - s)
        tmp = [0] * number_of_Pilots
        for interval in range(i + 1):
            tmp[s + interval] = 1
        frequency_Pattern.append(tmp)
# print(frequency_Pattern_top)
# for each column, calculate the number of assigned resource blocks
# this would be used to calculate the 'number of consecutive time slots' according to the 'payload' of traffic flow
frequency_Pattern_RB = [sum(i) for i in frequency_Pattern]
log_file.write('Number of pilots: %d \n' % number_of_Pilots)
log_file.write('Max allocation patterns: %d \n' % max_RBAllocationPatterns)
log_file.write('-' * 10 + 'Allocation Pattern' + '-' * 10 + '\n')
for i in range(number_of_Pilots):
    s = ''
    for j in range(max_RBAllocationPatterns):
        s += '%d ' % (frequency_Pattern[j][i])
    s += '\n'
    log_file.write(s)

# max_Len means the maximum value for the 'number of consecutive time slots'
max_Len = int(max([tf.delay_requirement for tf in list_of_TrafficFlows]))
# for simplicity, the maximum value of repetition is 1, so for each data packet only one replicas would be transmitted
max_K = 1
log_file.write('Max \'len\': \t')
log_file.write('%d  ' % max_Len)
log_file.write('\n')
log_file.write('Max \'K\': \t %d' % max_K)

needed_RB = [i.payload for i in list_of_TrafficFlows]
assert len(list_of_TrafficFlows) == len(needed_RB)
log_file.write('\n Calculating # of needed resource blocks... \n')
for i in range(len(list_of_TrafficFlows)):
    s = 'Index: %d \t # of RBs: %d \n' % (i, needed_RB[i])
    log_file.write(s)

# For simplicity, the number of needed replicas would be just 1, this corresponds to the MAX_K
needed_K = [1] * len(list_of_TrafficFlows)
assert len(list_of_TrafficFlows) == len(needed_K)
assert [needed_K[i] <= max_K for i in range(len(list_of_TrafficFlows))]
log_file.write('\n Calculating # of needed repetitions... \n')
for i in range(len(list_of_TrafficFlows)):
    s = 'Index: %d \t # of Ks: %d \n' % (i, needed_K[i])
    log_file.write(s)

# number of data packets for each TF
number_of_data_packets_TFs = []
number_of_configurations = []
for i in range(number_of_TrafficFlows):
    number_of_data_packets_TFs.append(math.floor(hyper_Period /
                                                 list_of_TrafficFlows[i].transmission_period))
    number_of_configurations.append(list_of_TrafficFlows[i].numberofconfigurations)

# print(number_of_data_packets_TFs)
# print(number_of_configurations)
# =======================================
# represent the resource grid

number_of_RBeachResourceGrid = hyper_Period
log_file.write('\n # of RBs per resource grid: %d \n' % number_of_RBeachResourceGrid)

# For each traffic flow, it owns a series of scheduling configurations
# for each scheduling configuration, it has seven features that have to be determined by the SMT solver:
# 0     Resource block allocation scheme
# 1     Offset (index of time slot for first transmission): 𝑜
# 2     # of consecutive time slots: 𝑙𝑒𝑛
# 3     # of repetitions: 𝑘∈{1, 2, 4, 8}
# 4     # interval between repetitions (# of slots): 𝑞
# 5     Periodicity: 𝑝
# 6     repeat number: r
# 7     valid indicator: v      then, SUM(r*v) == number of data packets per TF


# when creating the following "configuration_Series", use "number_of_configurations" to control
# the maximum number of configurations per TF directly.
max_Features_Configuration = 8
configuration_Series = [[[Int('conf%s_%s_%s' % (i, j, k))
                          for k in range(max_Features_Configuration)]
                         for j in range(number_of_configurations[i])]
                        for i in range(len(list_of_TrafficFlows))]
# for limiting the control overhead of the control configuration,
# there is only one control configuration for one application
# control_configuration = [[Int('control_conf_%s_%s' % (i, j))
#                           for j in range(max_Features_Configuration)]
#                          for i in range(len(list_of_TrafficFlows))]

# format of control configuration
# 0: resource allocation scheme
# 1: offset
# 2: len == 1
# 3: valid indicator: 0/1
control_configuration_max_features = 4
number_control_configuration = [ele - 1 for ele in number_of_configurations]
# print(number_control_configuration)
control_configuration = [[[Int('con_conf%s_%s_%s' % (i, j, k))
                           for k in range(control_configuration_max_features)]
                          for j in range(number_control_configuration[i])]
                         for i in range(len(list_of_TrafficFlows))]

s = Optimize()
# s = Solver()
log_file.write('\n' + '=' * 20 + 'CREATING SOLVER AND ADDING CONSTRAINTS' + '=' * 20 + '\n')

# additional constraint: this could be utilized to constraint the number of support traffic flows
# but in this version, this feature is ignored.
# valid_TrafficFlows = [Int('valid_TF%d' % i) for i in range(len(list_of_TrafficFlows))]
# log_file.write('The list the represent the valid of each traffic flow. if the value==1, '
#                'it means that the traffic flow can occupy the resource.')
# # ========== constraint for the list of valid indicators
# # Because not all the traffic flows can be supported, here for each traffic flow, a valid indicator
# # is set up. If the valid indicator == 1, then it means that it can be supported
# # Also, this is our optimization goal, the solver would maximize the 'SUM' of the list
# s.add(And([And(valid_TrafficFlows[i] >= 0,
#                valid_TrafficFlows[i] <= 1)
#            for i in range(len(list_of_TrafficFlows))]))
# log_file.write('Adding constraints: each valid indicator is 0 / 1')

# Add constraints for all parameters
# 1. constraint for 'RB allocation pattern'
for i in range(len(list_of_TrafficFlows)):
    con_RBAllocationPattern = And([And(configuration_Series[i][j][0] >= 0,
                                       configuration_Series[i][j][0] <= max_RBAllocationPatterns - 1)
                                   for j in range(number_of_configurations[i])])
    s.add(con_RBAllocationPattern)
    # for control
    s.add(And([And(control_configuration[i][j][0] >= 0,
                   control_configuration[i][j][0] <= max_RBAllocationPatterns - 1)
               for j in range(number_control_configuration[i])]))
    # s.add(And(control_configuration[i][0] >= 0, control_configuration[i][0] <= max_RBAllocationPatterns - 1))
log_file.write('Adding constraints: range of allocation patterns \n')

# 2. constraint for 'total amount of RBs'
translation_RB_Function = Function('translation_RB_Function', IntSort(), IntSort())
con_TranslationRBFunction = And([translation_RB_Function(i) == frequency_Pattern_RB[i]
                                 for i in range(max_RBAllocationPatterns)])
s.add(con_TranslationRBFunction)

# frequency pattern -- top
translation_RB_Top_Function = Function('translation_RB_Top_Function', IntSort(), IntSort())
con_TranslationRBTopFunction = And([translation_RB_Top_Function(i) == frequency_Pattern_top[i]
                                    for i in range(max_RBAllocationPatterns)])
s.add(con_TranslationRBTopFunction)

for i in range(len(list_of_TrafficFlows)):
    con_TotalAmountRBs = And([translation_RB_Function(configuration_Series[i][j][0])
                              * configuration_Series[i][j][2] >= needed_RB[i]
                              for j in range(number_of_configurations[i])])
    s.add(con_TotalAmountRBs)
    # for control
    s.add(And([translation_RB_Function(control_configuration[i][j][0]) *
               control_configuration[i][j][2] == list_of_TrafficFlows[i].control_overhead
               for j in range(number_control_configuration[i])]))
    # con = (translation_RB_Function(control_configuration[i][0]) * control_configuration[i][2]) == rbs_control
    # s.add(con)
log_file.write('Adding constraints: assigned RBs >= needed RBs \n')

# 3. constraint for 'number of repetition'
for i in range(len(list_of_TrafficFlows)):
    con_K = And([configuration_Series[i][j][3] == needed_K[i]
                 for j in range(number_of_configurations[i])])
    s.add(con_K)
    # for control
    # s.add(control_configuration[i][3] == 1)
log_file.write('Adding constraints: assigned Ks >= needed Ks \n')

# the 'sum_ValidCount' record the sum of 'valid count' for all scheduling configurations
# in the front of each scheduling configurations
# the main purpose is to align the scheduling configurations to all data packets so that
# the 'offset' in each scheduling configuration can be calculated easily and avoid ignore any data packet
# SUM(r*v) = total number of data packets per TF

sum_ValidCount = [Sum([configuration_Series[i][j][6] * configuration_Series[i][j][7]
                       for j in range(number_of_configurations[i])])
                  for i in range(len(list_of_TrafficFlows))]
for i in range(len(list_of_TrafficFlows)):
    s.add(sum_ValidCount[i] == number_of_data_packets_TFs[i])
log_file.write('Adding constraints:  sum of number of data packets \n')

# constraint on "valid indicator: v"
for i in range(len(list_of_TrafficFlows)):
    con = And([And(configuration_Series[i][j][7] >= 0,
                   configuration_Series[i][j][7] <= 1)
               for j in range(number_of_configurations[i])])
    s.add(con)
    # for control: all v ==  0/ 1
    # s.add(control_configuration[i][7] == 1)
    s.add(And([And(control_configuration[i][j][3] >= 0,
                   control_configuration[i][j][3] <= 1)
               for j in range(number_control_configuration[i])]))
log_file.write('Adding constraints: every "valid indicator == 0/1" \n')

# sum of valid indicator equal w.r.t control message and configuration
for i in range(len(list_of_TrafficFlows)):
    s.add(Sum([control_configuration[i][j][3]
               for j in range(number_control_configuration[i])]) + 1
          ==
          Sum([configuration_Series[i][j_][7] for j_ in range(number_of_configurations[i])]))

# 4. basic constraints for 'all parameters'
# 1) offset
for i in range(len(list_of_TrafficFlows)):
    con_Offset = And([configuration_Series[i][j][1] >= 0
                      for j in range(number_of_configurations[i])])
    # con_Offset_ = And([configuration_Series[i][j][1] > configuration_Series[i][j - 1][1]
    #                  for j in range(1, number_of_configurations[i])])
    s.add(con_Offset)
    # Offset for control
    # s.add(control_configuration[i][1] >= 0)
    # s.add(control_configuration[i][1] < hyper_period -1)
    s.add(And([control_configuration[i][j][1] >= 0
               for j in range(number_control_configuration[i])]))
# 2) len
for i in range(len(list_of_TrafficFlows)):
    con_Len = And([And(configuration_Series[i][j][2] >= 1, configuration_Series[i][j][2] <= max_Len)
                   for j in range(number_of_configurations[i])])
    s.add(con_Len)
    # Len for control
    # s.add(control_configuration[i][2] == 1)
    s.add(And([configuration_Series[i][j][2] == 1 for j in range(number_control_configuration[i])]))

# 3) k
for i in range(len(list_of_TrafficFlows)):
    con_K = And([And(configuration_Series[i][j][3] >= 1, configuration_Series[i][j][3] <= max_K)
                 for j in range(number_of_configurations[i])])
    s.add(con_K)
    # for control
    # s.add(control_configuration[i][3] == 1)
# 4) interval
for i in range(len(list_of_TrafficFlows)):
    # con_Interval = And([And(configuration_Series[i][j][4] >= 0, configuration_Series[i][j][4]
    #                         <= list_of_TrafficFlows[i].transmission_period)
    #                     for j in range(number_of_data_packets_TFs[i])])
    con_Interval = And([configuration_Series[i][j][4] == 0
                        for j in range(number_of_configurations[i])])
    s.add(con_Interval)
    # for control
    # s.add(control_configuration[i][4] == 0)
# 5) p
for i in range(len(list_of_TrafficFlows)):
    con_P = And([And(configuration_Series[i][j][5] >= 1,
                     configuration_Series[i][j][5] < 2 * list_of_TrafficFlows[i].transmission_period,
                     configuration_Series[i][j][5] < hyper_Period)
                 for j in range(number_of_configurations[i])])
    # con_P = And([configuration_Series[i][j][5] == 0
    #              for j in range(number_of_data_packets_TFs[i])])
    s.add(con_P)
    # for control
    # s.add(And(control_configuration[i][5] >= 1,
    #           control_configuration[i][5] < 2 * list_of_TrafficFlows[i].transmission_period,
    #           control_configuration[i][5] < hyper_period))

# 6) repeat number: r       r could be 1 or more
for i in range(len(list_of_TrafficFlows)):
    con_VC = And([And(configuration_Series[i][j][6] >= 1,
                      configuration_Series[i][j][6] <= number_of_data_packets_TFs[i])
                  for j in range(number_of_configurations[i])])
    # con_VC = And([And(configuration_Series[i][j][6] == 1)
    #               for j in range(number_of_configurations[i])])
    s.add(con_VC)
    # for control
    # s.add(And(control_configuration[i][6] == Sum([configuration_Series[i][j][7]
    #                                               for j in range(number_of_configurations[i])])))
log_file.write('Adding constraints: basic setting for each parameter \n')

# ========================== Resource mapping ===============================
# building the connection between configurations and Resource grid
# each traffic flow would occupy an empty and complete resource grid at first
# and then all resource grids will be combined (perform addition for each resource block)
# the goal is to keep all values lower than 1 which means that after considering all traffic flows that is valid
# each resource block can be assigned only once

# resource grid function arguments:
# 1. numbering of traffic flows [every traffic flow has a complete resource grid]
# 2. possible 'pos' [time resource: means the time slot because the resource grid is divided by time slots]
# 3. pilots/resource block         [frequency resource]
# 4. return value   [0/1, 0 means that the current resource block (using time resource and frequency resource
#                   to locate) isn't assigned for a specific traffic flow]
# Reason about why use 'Function' here:
# 'Function' can provide the mapping functionality between scheduling configuration and resource blocks
# Next, add constraints upon the input and output of the 'Function'

resource_grid_function = Function('resource_grid_function', IntSort(), IntSort(), IntSort(), IntSort())

# Constraints 1: return value should be within [0, 1]
con_range_resource_grid_function = And([And(resource_grid_function(tf, pos, pilot) >= 0,
                                            resource_grid_function(tf, pos, pilot) <= 1)
                                        for tf in range(len(list_of_TrafficFlows))
                                        for pos in range(number_of_RBeachResourceGrid)
                                        for pilot in range(number_of_Pilots)])
s.add(con_range_resource_grid_function)
log_file.write('Adding constraints: for each resource block, the value can only be 0/1 (use only once) \n')

# for control
resource_grid_function_control = Function('resource_grid_function_control', IntSort(), IntSort(), IntSort(), IntSort())
# Constraints 1: return value should be within [0, 1]
con_range_resource_grid_function_control = And([And(resource_grid_function_control(tf, pos, pilot) >= 0,
                                                    resource_grid_function_control(tf, pos, pilot) <= 1)
                                                for tf in range(len(list_of_TrafficFlows))
                                                for pos in range(number_of_RBeachResourceGrid)
                                                for pilot in range(number_of_Pilots)])
s.add(con_range_resource_grid_function_control)
log_file.write('Adding constraints: for each resource block, the value can only be 0/1 (use only once)_ for control \n')

# for i in range(len(list_of_TrafficFlows)):
#     for j in range(number_of_configurations[i]):
#         con_ = Implies(
#             configuration_Series[i][j][7] == 1,
#             And(configuration_Series[i][j][1]
#                 >= list_of_TrafficFlows[i].initial_time +
#                 (Sum([configuration_Series[i][j_][6] * configuration_Series[i][j_][7] for j_ in range(j)])) *
#                 list_of_TrafficFlows[i].transmission_period,
#                 configuration_Series[i][j][1] + configuration_Series[i][j][2]
#                 <= list_of_TrafficFlows[i].initial_time +
#                 (Sum([configuration_Series[i][j_][6] * configuration_Series[i][j_][7] for j_ in range(j)]) + 1) *
#                 list_of_TrafficFlows[i].transmission_period))
#         s.add(con_)
#         # print(con_)
#         # an additional constraint: border of the hyper-period
#
#         con_b = Implies(configuration_Series[i][j][7] == 1,
#                         configuration_Series[i][j][1] + configuration_Series[i][j][2] <= hyper_Period)
#         s.add(con_b)
log_file.write('Adding constraints: arrival time \n')
log_file.write('Adding constraints: deadline \n')

for i in range(len(list_of_TrafficFlows)):
    for j in range(number_of_configurations[i]):
        for k in range(1, number_of_data_packets_TFs[i] + 1):
            con_ = Implies(
                And(configuration_Series[i][j][6] == k, configuration_Series[i][j][7] == 1),
                And([And(configuration_Series[i][j][1] + k_ * configuration_Series[i][j][5]
                         >= list_of_TrafficFlows[i].initial_time +
                         (Sum([configuration_Series[i][j_][6] * configuration_Series[i][j_][7]
                               for j_ in range(j)]) + k_) *
                         list_of_TrafficFlows[i].transmission_period,
                         configuration_Series[i][j][1] +
                         configuration_Series[i][j][2] * configuration_Series[i][j][3] +
                         configuration_Series[i][j][4] * (configuration_Series[i][j][3] - 1) +
                         k_ * configuration_Series[i][j][5] - 1
                         <= list_of_TrafficFlows[i].initial_time +
                         (Sum([configuration_Series[i][j_][6] * configuration_Series[i][j_][7]
                               for j_ in range(j)]) + k_) * list_of_TrafficFlows[i].transmission_period +
                         list_of_TrafficFlows[i].delay_requirement)
                     for k_ in range(k)]))
            s.add(con_)
        con_b = Implies(configuration_Series[i][j][7] == 1,
                        configuration_Series[i][j][1] + configuration_Series[i][j][2] <= hyper_Period)
        s.add(con_b)

# # for storing the start time of each valid configuration
# start_time_valid_configuration = [Int('start_time_valid_configuration_%s_%s' % (i, j))
#                          for j in range(max_Features_Configuration)
#                          for i in range(len(list_of_TrafficFlows))]
# for i in range(len(list_of_TrafficFlows)):

# control message sending before each configuration
# for control
# for i in range(len(list_of_TrafficFlows)):
#     for j in range(number_of_configurations[i]):
#         for k in range(0, j+1):
#             con = Implies(And(configuration_Series[i][j][7] == 1,
#                               Sum([configuration_Series[i][j_][7] for j_ in range(j)]) == k),
#                           control_configuration[i][1] + control_configuration[i][5] * k <
#                           configuration_Series[i][j][1])
#             s.add(con)
# print(con)
# print('\n')
# Step 0: let the first valid indicator of data configuration equals to 1
s.add(And([configuration_Series[i][0][7] == 1 for i in range(len(list_of_TrafficFlows))]))
# Step 1: let the valid indicator equal [control & configuration]
# Step 2: for every valid pair, set constraint
for i in range(len(list_of_TrafficFlows)):
    for j in range(1, number_of_configurations[i]):
        s.add(control_configuration[i][j - 1][3] == configuration_Series[i][j][7])
        s.add(control_configuration[i][j - 1][1] < configuration_Series[i][j][1])

# resource grid flag function arguments:
# 1. numbering of traffic flows [every traffic flow has a complete resource grid]
# 2. possible 'pos' [time resource: means the time slot because the resource grid is divided by time slots]
# 3. return value   [0/1]
# Reason:
# 'resource_grid_flag_function' (RGFF) is an auxiliary function of 'resource_grid_function' (RGF)
# when we use scheduling configurations to determine whether a 'pos' would be assigned
# it's easy to record assignment status of the pilots ['resource block allocation scheme'] in the current 'pos'
# but for other idle 'pos', the RGF don't know how to handle the value of each location
# so that we have to guarantee that all resource blocks in idle 'pos' equal to 0

resource_grid_flag_function = Function('resource_grid_flag_function', IntSort(), IntSort(), IntSort())

# Constraints 1: return value should be within [0, 1]
con_range_resource_grid_flag_function = And([And(resource_grid_flag_function(tf, pos) >= 0,
                                                 resource_grid_flag_function(tf, pos) <= 1)
                                             for tf in range(len(list_of_TrafficFlows))
                                             for pos in range(number_of_RBeachResourceGrid)])
s.add(con_range_resource_grid_flag_function)

# For 'pos' that hasn't been impacted, all resource block values should be 0
for i in range(len(list_of_TrafficFlows)):
    for pos in range(number_of_RBeachResourceGrid):
        s.add(Implies(resource_grid_flag_function(i, pos) == 0,
                      And([resource_grid_function(i, pos, j) == 0 for j in range(number_of_Pilots)])))
        s.add(Implies(resource_grid_flag_function(i, pos) == 1,
                      Sum([resource_grid_function(i, pos, j)
                           for j in range(number_of_Pilots)]) >= 1))

# for control
resource_grid_flag_function_control = Function('resource_grid_flag_function_control', IntSort(), IntSort(), IntSort())

# Constraints 1: return value should be within [0, 1]
con_range_resource_grid_flag_function_control = And([And(resource_grid_flag_function_control(tf, pos) >= 0,
                                                         resource_grid_flag_function_control(tf, pos) <= 1)
                                                     for tf in range(len(list_of_TrafficFlows))
                                                     for pos in range(number_of_RBeachResourceGrid)])
s.add(con_range_resource_grid_flag_function_control)

# For 'pos' that hasn't been impacted, all resource block values should be 0
for i in range(len(list_of_TrafficFlows)):
    for pos in range(number_of_RBeachResourceGrid):
        s.add(Implies(resource_grid_flag_function_control(i, pos) == 0,
                      And([resource_grid_function_control(i, pos, j) == 0 for j in range(number_of_Pilots)])))
        s.add(Implies(resource_grid_flag_function_control(i, pos) == 1,
                      Sum([resource_grid_function_control(i, pos, j)
                           for j in range(number_of_Pilots)]) >= 1))

# for traffic flow that is invalid, all resource block values should be 0
# for i in range(len(list_of_TrafficFlows)):
#     s.add(And([resource_grid_function(i, pos, n_) == 0
#                for pos in range(number_of_RBeachResourceGrid)
#                for n_ in range(number_of_Pilots)]))
#     s.add(And([resource_grid_flag_function(i, pos) == 0
#                for pos in range(number_of_RBeachResourceGrid)]))

# the number of 'impacted' pos should equal to the needed number for each traffic flow
for i in range(len(list_of_TrafficFlows)):
    s.add(And([And([Sum([resource_grid_flag_function(i, pos) for pos in
                         range(number_of_RBeachResourceGrid)])
                    == (Sum([configuration_Series[i][j][2] *
                             configuration_Series[i][j][3] *
                             configuration_Series[i][j][6] *
                             configuration_Series[i][j][7]
                             for j in range(number_of_configurations[i])]))])]))

# for control
for i in range(len(list_of_TrafficFlows)):
    s.add(And([And([Sum([resource_grid_flag_function_control(i, pos) for pos in
                         range(number_of_RBeachResourceGrid)])
                    == (Sum([control_configuration[i][j][3] * control_configuration[i][j][2]
                             for j in range(number_control_configuration[i])]))])]))

# Calculate the position of each resource block according to all scheduling configurations
for i in range(len(list_of_TrafficFlows)):
    for j in range(number_of_configurations[i]):
        for k in range(1, number_of_data_packets_TFs[i] + 1):
            if verbose:
                print('Adding constraints: %d %d' % (i, j))
            con_ = And([Implies(And(
                configuration_Series[i][j][2] == m,
                configuration_Series[i][j][0] == n,
                configuration_Series[i][j][7] == 1,
                configuration_Series[i][j][6] == k),
                And([And(And([resource_grid_function(i,
                                                     configuration_Series[i][j][1] +
                                                     m_ +
                                                     k_ * configuration_Series[i][j][5],
                                                     n_) == frequency_Pattern[n][n_]
                              for n_ in range(number_of_Pilots)]),
                         resource_grid_flag_function(i, configuration_Series[i][j][1] +
                                                     m_ + k_ * configuration_Series[i][j][5]) == 1)
                     for k_ in range(k)
                     for m_ in range(m)]))
                # for ll in range(1, max_K + 1)
                for m in range(1, max_Len + 1)
                for n in range(max_RBAllocationPatterns)])
            s.add(con_)

# for control
# for i in range(len(list_of_TrafficFlows)):
#     for k in range(1, number_of_configurations[i] + 1):
#         con = And([Implies(And(control_configuration[i][0] == n,
#                                control_configuration[i][6] == k),
#                            And([And(And([resource_grid_function_control(i,
#                                                                         control_configuration[i][1] +
#                                                                         k_ * control_configuration[i][5],
#                                                                         n_) == frequency_Pattern[n][n_]
#                                          for n_ in range(number_of_Pilots)]),
#                                     resource_grid_flag_function_control(i,
#                                                                         control_configuration[i][1]
#                                                                         + k_ * control_configuration[i][5]) == 1)
#                                 for k_ in range(k)]))
#                    for n in range(max_RBAllocationPatterns)])
#         s.add(con)
# ignore the 'len'  == 1
for i in range(len(list_of_TrafficFlows)):
    for j in range(number_control_configuration[i]):
        s.add(And([Implies(And(control_configuration[i][j][3] == 1,
                               control_configuration[i][j][0] == n),
                           And(And([resource_grid_function_control(i, control_configuration[i][j][1] + 0, n_)
                                    == frequency_Pattern[n][n_]
                                    for n_ in range(number_of_Pilots)]),
                               resource_grid_flag_function_control(i, control_configuration[i][j][1]) == 1))
                   for n in range(max_RBAllocationPatterns)]))

# For each resource block, it can be used only once
for pos in range(number_of_RBeachResourceGrid):
    for p in range(number_of_Pilots):
        s.add(Sum([(resource_grid_function(i, pos, p) +
                    resource_grid_function_control(i, pos, p))
                   for i in range(len(list_of_TrafficFlows))]) <= 1)
log_file.write('Adding constraints: after assigning, each RB can only be used once \n')

time_ConstraintsFinished = datetime.now()
ss = 'Adding constraints finished: %s\n' % time_ConstraintsFinished
print(ss)
log_file.write(ss)
ss = 'Time elapsed - Adding constraints: %s\n' % (time_ConstraintsFinished - time_SystemStart)
print(ss)
log_file.write(ss)

# supporting all traffic flows
# s.add(And([valid_TrafficFlows[i] == 1 for i in range(len(valid_TrafficFlows))]))

# Optimization goal: minimize the used pilots

max_frequency_pattern = Int('max_frequency_pattern')
s.add(And([Implies(configuration_Series[i][j][7] == 1,
                   max_frequency_pattern >=
                   translation_RB_Top_Function(configuration_Series[i][j][0]))
           for i in range(len(list_of_TrafficFlows))
           for j in range(number_of_configurations[i])]))

s.add(And([Implies(control_configuration[i][j][3] == 1,
                   max_frequency_pattern >= translation_RB_Top_Function(control_configuration[i][j][0]))
           for i in range(len(list_of_TrafficFlows))
           for j in range(number_control_configuration[i])]))

print('optimization...')
s.minimize(max_frequency_pattern)

# enable_trace(max_frequency_pattern)

# c represent the number of solutions we want to get
# but here, the exclusion of current solution hasn't been done [no need to do that]
c = 1
log_file.write('\n' + '=' * 20 + 'RESULTS' + '=' * 20 + '\n')
pre_time = datetime.now()
max_pilots = 0
# s.check()
# The real number of conf.
sum_conf = 0
# while s.check() == sat:
while s.check() == sat:
    c -= 1
    if c < 0:
        break
    m = s.model()

    post_time = datetime.now()
    oos = post_time - pre_time
    ss = 'Obtaining one solution: %s \n' % oos
    print(ss)
    log_file.write(ss)
    pre_time = post_time

    log_file.write('\n Valid indicator for each traffic flow: \n')
    # valid_TrafficFlows_int = []
    ss = ''
    # for i in range(len(list_of_TrafficFlows)):
    #     tmp = m.evaluate(valid_TrafficFlows[i]).as_long()
    #     valid_TrafficFlows_int.append(tmp)
    #     ss += '%d:\t%d\n' % (i, tmp)
    # log_file.write(ss + '\n')

    for i in range(len(list_of_TrafficFlows)):
        log_file.write('\n Resource grid FLAG for traffic flow %d ... \n' % i)
        ss = ''
        for j in range(number_of_RBeachResourceGrid):
            ss += '%d ' % m.evaluate(resource_grid_flag_function(i, j)).as_long()
        ss += '\n'
        log_file.write(ss)

    for i in range(len(list_of_TrafficFlows)):
        log_file.write('\n Resource grid for traffic flow %d ... \n' % i)
        for j in range(number_of_Pilots):
            ss = ''
            for k in range(number_of_RBeachResourceGrid):
                ss += '%d ' % m.evaluate(resource_grid_function(i, k, j)).as_long()
            ss += '\n'
            log_file.write(ss)

    for i in range(len(list_of_TrafficFlows)):
        log_file.write('\n (Control) Resource grid FLAG for traffic flow %d ... \n' % i)
        ss = ''
        for j in range(number_of_RBeachResourceGrid):
            ss += '%d ' % m.evaluate(resource_grid_flag_function_control(i, j)).as_long()
        ss += '\n'
        log_file.write(ss)

    for i in range(len(list_of_TrafficFlows)):
        log_file.write('\n (Control) Resource grid for traffic flow %d ... \n' % i)
        for j in range(number_of_Pilots):
            ss = ''
            for k in range(number_of_RBeachResourceGrid):
                ss += '%d ' % m.evaluate(resource_grid_function_control(i, k, j)).as_long()
            ss += '\n'
            log_file.write(ss)

    # for i in range(len(list_of_TrafficFlows)):
    #     log_file.write('\n Configuration series for traffic flow %d ... \n' % i)
    #     for j in range(number_of_configurations[i]):
    #         if m.evaluate(configuration_Series[i][j][7]).as_long() == 1:
    #             ss = 'Allocation scheme: %d \n' % m.evaluate(configuration_Series[i][j][0]).as_long() + \
    #                  'Offset: %d \n' % m.evaluate(configuration_Series[i][j][1]).as_long() + \
    #                  'len: %d \n' % m.evaluate(configuration_Series[i][j][2]).as_long() + \
    #                  'K: %d \n' % m.evaluate(configuration_Series[i][j][3]).as_long() + \
    #                  'Interval: %d \n' % m.evaluate(configuration_Series[i][j][4]).as_long() + \
    #                  'Periodicity: %d \n' % m.evaluate(configuration_Series[i][j][5]).as_long() + \
    #                  'Repeat number: %d \n' % m.evaluate(configuration_Series[i][j][6]).as_long() + \
    #                  'Valid indicator: %d \n' % m.evaluate(configuration_Series[i][j][7]).as_long() + '\n'
    #             log_file.write(ss)
    for i in range(len(list_of_TrafficFlows)):
        log_file.write('\n Configuration series for traffic flow %d ... \n' % i)
        # for one application, the actual number of conf.
        part_sum_conf = 0
        for j in range(number_of_configurations[i]):
            ss = 'Allocation scheme: %d \n' % m.evaluate(configuration_Series[i][j][0]).as_long() + \
                 'Offset: %d \n' % m.evaluate(configuration_Series[i][j][1]).as_long() + \
                 'len: %d \n' % m.evaluate(configuration_Series[i][j][2]).as_long() + \
                 'K: %d \n' % m.evaluate(configuration_Series[i][j][3]).as_long() + \
                 'Interval: %d \n' % m.evaluate(configuration_Series[i][j][4]).as_long() + \
                 'Periodicity: %d \n' % m.evaluate(configuration_Series[i][j][5]).as_long() + \
                 'Repeat number: %d \n' % m.evaluate(configuration_Series[i][j][6]).as_long() + \
                 'Valid indicator: %d \n' % m.evaluate(configuration_Series[i][j][7]).as_long()
            log_file.write(ss)
            part_sum_conf += m.evaluate(configuration_Series[i][j][7]).as_long()
            sum_conf += m.evaluate(configuration_Series[i][j][7]).as_long()
        ss = 'Application %d: Maximum allowed conf: %d, actual conf: %d \n' % \
             (i,
              list_of_TrafficFlows[i].numberofconfigurations,
              part_sum_conf)
        log_file.write(ss)

        log_file.write('\n Configuration for control of traffic flow %d ... \n' % i)
        for j in range(number_control_configuration[i]):
            ss = 'Allocation scheme: %d \n' % m.evaluate(control_configuration[i][j][0]).as_long() + \
                 'Offset: %d \n' % m.evaluate(control_configuration[i][j][1]).as_long() + \
                 'len: %d \n' % m.evaluate(control_configuration[i][j][2]).as_long() + \
                 'Valid indicator: %d \n' % m.evaluate(control_configuration[i][j][3]).as_long() + '\n'
            log_file.write(ss)

    # log_file_.write('%d %f \n%s \n%s \n' % (sum(valid_TrafficFlows_int),
    #                                         (sum(valid_TrafficFlows_int) / number_of_TrafficFlows),
    #                                         (time_ConstraintsFinished - time_SystemStart),
    #                                         oos))
    max_pilots = m.evaluate(max_frequency_pattern).as_long()
    ss = 'Max pilot: %d' % max_pilots + '\n'
    print(ss)
    log_file.write(ss)
    ss = 'Maximum allowed number of conf.: %d \n' % sum_maximum_conf
    log_file.write(ss)
    ss = 'Actual number of conf.: %d \n' % sum_conf
    log_file.write(ss)

    log_file_.write('%d\n' % number_of_TrafficFlows)
    for i in range(number_of_TrafficFlows):
        ss = '%d %d %d %d\n' % (list_of_TrafficFlows[i].initial_time,
                                list_of_TrafficFlows[i].transmission_period,
                                list_of_TrafficFlows[i].payload,
                                list_of_TrafficFlows[i].delay_requirement)
        log_file_.write(ss)
    log_file_.write('%d\n' % number_of_Pilots)
    log_file_.write('%d\n' % hyper_Period)
    log_file_.write('%d\n' % sum_conf)
    log_file.close()
    log_file_.close()
    # success or fail
    SoF = True
else:
    post_time = datetime.now()
    oos = post_time - pre_time
    ss = 'Fail time: %s \n' % oos
    print(ss)
    log_file_.write('fail')
    # print('fail to solve.')
    log_file.close()
    log_file_.close()
    # success or fail
    SoF = False

slovingTime = datetime.now() - timeSystemStart
print(slovingTime, file=log_solvingtime)
if SoF:
    print('%d %d %d %d' % (noseries, max_pilots, sum_maximum_conf, sum_conf), file=log_pilots)
else:
    print(SoF, file=log_pilots)
