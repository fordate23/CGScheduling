# The file is for calculating the number of resource units for control overhead
# For more information, please refer to the paper
# G. Pocovi, K. I. Pedersen, and P. Mogensen,
# “Joint link adaptation and scheduling for 5g ultra-reliable low-latency communications,”
# Ieee Access, vol. 6, pp. 28 912–28 922, 2018.

sinr_to_control_rbs = [[-2.2, 14], [0.2, 8], [4.2, 5]]


# return resource units for control based on sinr
def getcontrolrbs(sinr):
    if sinr > sinr_to_control_rbs[-1][0]:
        return 3
    else:
        for i in range(len(sinr_to_control_rbs)):
            if sinr_to_control_rbs[i][0] >= sinr:
                return sinr_to_control_rbs[i][1]
