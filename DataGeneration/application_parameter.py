import math
from network_parameter import *
from sinrtobits import *
import numpy as np

# This is for the settings of applications. The data is from QoS requirements of some industrial 4.0 applications.

# total number of applications/ traffic flow
max_applications = 4
length_timeslot = 0.5   # (ms)

# define characteristics of application [transmission period (ms), payload (bytes), latency (ms)]
# The following is for small scale testing...
application1 = [5, 20, 3]
application2 = [10, 120, 6]  # the original setting of payload would be 1K bytes, here we use a small value for demo
application3 = [2, 40, 1]
applications_collection = [application1, application2, application3]


# return a list of tested applications based on applications_collection
# characteristics of each application:
# [offset, transmission period, payload (#. resource units), latency, # of conf., control overhead]
# rule of offset: offset + latency <= transmission period
# rule of # of conf.: range [1, maximum # of data packets] or Manually defined
# According to the paper, we assume that maximum number of configurations == maximum number of data packets
# everything should be normalized to the length of time slot
def generating_application_info():
    list_of_application = []
    number_of_applications = len(applications_collection)
    for i in range(max_applications):
        application_id = random.randint(0, number_of_applications - 1)
        transmission_period = int(applications_collection[application_id][0] / length_timeslot)
        payload = applications_collection[application_id][1] * 8    # to bits
        latency = int(applications_collection[application_id][2] / length_timeslot)
        # generate SINR value for each applications
        sinr = getsinr()
        # obtain # of resource units for each application
        payload_resource_unit = math.ceil((payload / getbits(sinr)))

        # number of packets == maximum number of configurations
        number_of_configurations_max = 0

        # generate the offset
        offset_max = transmission_period - latency
        offset = random.randint(0, max(offset_max, 0))
        if offset_max <= 0:
            offset = 0

        # for each control message, it consumes 1 resource unit
        control_overhead = 1

        list_of_application.append([offset,
                                    transmission_period,
                                    payload_resource_unit,
                                    latency,
                                    number_of_configurations_max,
                                    control_overhead])
    tp_list = [ele[1] for ele in list_of_application]
    hyper_period = np.lcm.reduce(tp_list)
    # Update the information of "maximum number of configurations"
    for i in range(len(list_of_application)):
        list_of_application[i][4] = hyper_period / list_of_application[i][1]

    return hyper_period, list_of_application

