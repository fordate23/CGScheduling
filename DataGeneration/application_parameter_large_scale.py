# This file is for the generation of traffic flows for the large scale scenario.
import math
from network_parameter import *
from sinrtobits import *
from control_overhead import *
import numpy as np

# The fundamental settings
tp_min = 2  # the minimum value of the transmission period (ms)
tp_max = 8  # the maximum value of the transmission period (ms)
payload_min = 512  # the minimum value of the payload (bytes)
payload_max = 1024  # the maximum value of the payload (bytes)

# the ratio between latency requirement and transmission period
delay_min = 0.8  # the minimum value of the ratio
delay_max = 1.0  # the maximum value of the ratio

# length of each time slot
length_timeslot = 0.125


# return a list of tested applications based on applications_collection
# characteristics of each application:
#   [offset, transmission period, payload (#. resource units), latency, # of conf.]
# rule of offset: offset + latency <= transmission period
# rule of # of conf.: range [1, maximum # of data packets] or Manually defined
# everything should be normalized to the length of time slot

def generating_application_info(max_applications):
    list_of_application = []
    for i in range(max_applications):
        transmission_period = int(np.random.randint(tp_min, tp_max + 1) / length_timeslot)
        payload = np.random.randint(payload_min, payload_max + 1)
        latency = max(1, int(np.random.randint(int(delay_min * transmission_period),
                                               int(delay_max * transmission_period))))
        sinr = getsinr()
        payload_resource_unit = math.ceil((payload / getbits(sinr)))

        number_of_configurations_max = 0

        offset_max = transmission_period - latency
        offset = random.randint(0, max(offset_max, 0))
        if offset_max <= 0:
            offset = 0

        control_overhead = getcontrolrbs(sinr)

        list_of_application.append([offset,
                                    transmission_period,
                                    payload_resource_unit,
                                    latency,
                                    number_of_configurations_max,
                                    control_overhead])
    tp_list = [ele[1] for ele in list_of_application]
    hyper_period = np.lcm.reduce(tp_list)
    for i in range(len(list_of_application)):
        list_of_application[i][4] = hyper_period / list_of_application[i][1]

    return hyper_period, list_of_application