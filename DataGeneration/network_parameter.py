# This is for the settings of wireless communication.
# Here, we only assume the range of SNR rather than build a complex wireless communication channel model due to the fact
# that we only perform scheduling operation while not performing real data-transmission.
import random

# settings for the range of SINR value
min_sinr = 2
max_sinr = 20


# return a random sinr value according to the range
def getsinr():
    return random.uniform(min_sinr, max_sinr)
