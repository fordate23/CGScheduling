# This file is for the conversion from SINR to bits per resource unit.
# For more details, please refer to the paper:
# J. Garc ́ıa-Morales, M. C. Lucas-Estan ̃, and J. Gozalvez,
# “Latency- sensitive 5g ran slicing for industry 4.0,”
# IEEE Access, vol. 7, pp. 143 139–143 159, 2019.

sinr_to_bits_list = [[-0.4167, 16],
                     [1.0417, 24], [1.6667, 32], [2.9167, 40], [3.5417, 56],
                     [5.0000, 72], [5.6250, 88], [7.0833, 104], [7.9167, 120],
                     [8.7500, 136], [10.8333, 144], [11.6667, 144], [12.9167, 176],
                     [13.3333, 208], [14.5000, 224], [15.0000, 256], [15.8333, 280],
                     [15.9167, 328], [16.0000, 336], [16.2917, 376], [16.8750, 408],
                     [18.6667, 408], [19.7917, 440], [20.4167, 488], [21.0417, 520],
                     [21.4167, 552], [22.7083, 584], [24.5000, 616], [25.8333, 712]]


# return bits for sinr
def getbits(sinr):
    # premises: sinr must >-0.4167
    if sinr > sinr_to_bits_list[-1][0]:
        return 712
    else:
        for i in range(len(sinr_to_bits_list)):
            if sinr_to_bits_list[i][0] >= sinr:
                return sinr_to_bits_list[i][1]

# print(getbits(10))
