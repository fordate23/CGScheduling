import numpy as np
import math
import statistics

# 0: theoretical    1: Heuristic
which_category = 0

confname = ['COmax', '1']
# folder_name = ['lowload0.40.6-0.5-*5','lowload0.40.6-0.5', 'midload0.40.6-0.5', 'highload0.40.6-0.5',
#                'highload0.40.6-0.25', 'highload0.6-0.8-0.5', 'highload0.40.6-0.125']
# folder_name = ['mid0.10.2', 'high0.10.2', 'mid0.10.2-20', 'mid0.10.2-30',  # 4
#                'mid0.10.2-40', 'mid0.10.2-50', 'mid0.10.2-15', 'mid0.10.2-25',  # 4
#                'mid0.10.2-35', 'mid0.10.2-45']
# file_root = 'NewLS/0.4-0.6/'
# file_root = 'NewLS/0.1-0.2/'
# file_root = 'NewLS/0.2-0.4/'
# file_root = 'NewLS/0.6-0.8/'
# file_root = 'NewLS/0.2-0.4/0.25'
# file_root = 'NewLS/0.4-0.6/'
# file_root = 'nolimitation/0.1-0.2/'
# file_root = 'nolimitation/0.2-0.4/'
# file_root = 'nolimitation/0.1-0.2/'
# file_root = 'nolimitation/0.1-0.2/'
file_root = 'nolimitation/0.8-1.0/'
# file_root = 'NewLS/0.2-0.4/'
# file_root = 'NewLS/0.6-1.0/'
folder_name = ['10', '20', '30', '40', '50', '60', '70']

# 0.1-0.2
# maximum_pilots = [11, 15, 20, 22, 25, 29, 31, 34]

# 0.2-0.4
# maximum_pilots = [8, 13, 17, 20, 23, 26, 28, 29]

# 0.4-0.6
# maximum_pilots = [7, 12, 15, 18, 20, 24, 27]

# 0.6-0.8
# maximum_pilots = [7, 10, 15, 16, 20, 22, 26]

# 0.8-1.0
maximum_pilots = [6, 10, 13, 17, 19, 22, 24]



parent_folder = 0


def Theoretical():
    r_p = []
    r_e = []
    r_s = []
    p_success = []
    success_ratio = []
    e_success = []
    for which_folder in range(len(folder_name)):
        pilots = []
        efficiency = []
        pilots_success = []
        eff_success = []
        success = 0
        filename = file_root+'naive_%s.txt' % (folder_name[which_folder])
        with open(filename, 'r') as f:
            lines = f.readlines()
        for line in lines:
            l = line.strip('\n').split(' ')
            tmp_p = int(l[0])
            pilots.append(tmp_p)
            efficiency.append(float(l[1]))
            if tmp_p < maximum_pilots[which_folder]:
                pilots_success.append(tmp_p)
                eff_success.append(float(l[1]))
                success += 1
        success_ratio.append(success/len(pilots))
        p_success.append(np.mean(pilots_success))
        e_success.append(np.mean(eff_success))

        r_p.append(np.mean(pilots))
        r_e.append(np.mean(efficiency))

        solvingtime = []
        filename = file_root+'solvingtime_%s.txt' % (folder_name[which_folder])
        with open(filename, 'r') as f:
            lines = f.readlines()
        for line in lines:
            l = line.strip('\n').split(' ')
            solvingtime.append(float(l[0]))

        r_s.append(np.mean(solvingtime))

    # print('Average pilots: %f ' % np.mean(pilots))
    # print('Max pilots: %f ' % max(pilots))
    # print('Efficiency (data): %f' % np.mean(efficiency))
    # print('%.2f  %.4f' % (np.mean(pilots), np.mean(efficiency)))
    s = 'all_average_pilots: \n'
    for ele in r_p:
        s += ' %.2f' % ele
    print(s)
    s = 'all_average_efficiency: \n'
    for ele in r_e:
        s += ' %.4f' % ele
    print(s)

    s = 'all_average_solvingtime: \n'
    for ele in r_s:
        s += ' %.2f' % ele
    print(s)

    s = 'success_average_ratio: \n'
    for ele in success_ratio:
        s += ' %.2f' % ele
    print(s)

    s = 'success_average_pilots: \n'
    for ele in p_success:
        s += ' %.4f' % ele
    print(s)

    s = 'success_average_efficiency: \n'
    for ele in e_success:
        s += ' %.4f' % ele
    print(s)


def Heuristic_1():
    r_p = []
    r_e = []
    r_ms = []
    r_packets = []

    p_success = []
    success_ratio = []
    e_success = []
    for which_folder in range(len(folder_name)):
        pilots = []
        efficiency = []

        ms = []
        packets = []

        pilots_success = []
        eff_success = []
        success = 0
        filename = file_root+'1/pilots_%s.txt' % folder_name[which_folder]
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            l = line.strip('\n').split(' ')
            tmp_p = int(l[0])
            pilots.append(tmp_p)
            efficiency.append(float(l[1]))
            if tmp_p < maximum_pilots[which_folder]:
                pilots_success.append(tmp_p)
                eff_success.append(float(l[1]))
                success += 1
        success_ratio.append(success / len(pilots))
        p_success.append(np.mean(pilots_success))
        e_success.append(np.mean(eff_success))

        r_p.append(np.mean(pilots))
        r_e.append(np.mean(efficiency))

        filename = file_root+'1/solvingtime_%s.txt' % folder_name[which_folder]
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            l = line.strip('\n').split(' ')
            ms.append(float(l[0]))
            packets.append(int(l[1]))

        r_ms.append(np.mean(ms))
        r_packets.append(np.mean(packets))

        # print('Variance: %f' % statistics.variance(pilots))
    # print('Average pilots: %f' % (np.mean(pilots)))
    # print('Max pilots: %f' % max(pilots))
    # print('Average efficiency: %f' % (np.mean(efficiency)))
    # print('Average ratio between actial conf. and allowed conf.: %f' % np.mean(ratio_actual_allowed))
    # print('Real number of conf.: %f' % np.mean(real_conf))
    s = 'allaveragepilots: \n'
    for ele in r_p:
        s += ' %.2f' % ele
    print(s)
    s = 'allaverageefficiency: \n'
    for ele in r_e:
        s += ' %.4f' % ele
    print(s)

    s = 'allaveragesolvingtime: \n'
    for ele in r_ms:
        s += ' %.2f' % ele
    print(s)

    s = 'allaveragepackets: \n'
    for ele in r_packets:
        s += ' %d' % ele
    print(s)

    s = 'successaverageratio: \n'
    for ele in success_ratio:
        s += ' %.2f' % ele
    print(s)

    s = 'successaveragepilots: \n'
    for ele in p_success:
        s += ' %.4f' % ele
    print(s)

    s = 'successaverageefficiency: \n'
    for ele in e_success:
        s += ' %.4f' % ele
    print(s)


def Heuristic_nolimitation():
    r_p = []
    r_e = []
    r_ms = []
    r_packets = []

    p_success = []
    success_ratio = []
    e_success = []
    for which_folder in range(len(folder_name)):
        pilots = []
        efficiency = []

        ms = []
        packets = []

        pilots_success = []
        eff_success = []
        success = 0
        filename = file_root+'COmax/pilots_%s.txt' % folder_name[which_folder]
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            l = line.strip('\n').split(' ')
            tmp_p = int(l[0])
            pilots.append(tmp_p)
            efficiency.append(float(l[1]))
            if tmp_p < maximum_pilots[which_folder]:
                pilots_success.append(tmp_p)
                eff_success.append(float(l[1]))
                success += 1
        success_ratio.append(success / len(pilots))
        p_success.append(np.mean(pilots_success))
        e_success.append(np.mean(eff_success))

        r_p.append(np.mean(pilots))
        r_e.append(np.mean(efficiency))

        filename = file_root+'COmax/solvingtime_%s.txt' % folder_name[which_folder]
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            l = line.strip('\n').split(' ')
            ms.append(float(l[0]))
            packets.append(int(l[1]))

        r_ms.append(np.mean(ms))
        r_packets.append(np.mean(packets))

        # print('Variance: %f' % statistics.variance(pilots))
    # print('Average pilots: %f' % (np.mean(pilots)))
    # print('Max pilots: %f' % max(pilots))
    # print('Average efficiency: %f' % (np.mean(efficiency)))
    # print('Average ratio between actial conf. and allowed conf.: %f' % np.mean(ratio_actual_allowed))
    # print('Real number of conf.: %f' % np.mean(real_conf))
    s = 'allaveragepilots: \n'
    for ele in r_p:
        s += ' %.2f' % ele
    print(s)
    s = 'allaverageefficiency: \n'
    for ele in r_e:
        s += ' %.4f' % ele
    print(s)

    s = 'allaveragesolvingtime: \n'
    for ele in r_ms:
        s += ' %.2f' % ele
    print(s)

    s = 'allaveragepackets: \n'
    for ele in r_packets:
        s += ' %d' % ele
    print(s)

    s = 'successaverageratio: \n'
    for ele in success_ratio:
        s += ' %.2f' % ele
    print(s)

    s = 'successaveragepilots: \n'
    for ele in p_success:
        s += ' %.4f' % ele
    print(s)

    s = 'successaverageefficiency: \n'
    for ele in e_success:
        s += ' %.4f' % ele
    print(s)



print('Naive:')
Theoretical()
print('*'*30)
print()

print('COmax:')
Heuristic_nolimitation()
print()
print('1:')
Heuristic_1()
