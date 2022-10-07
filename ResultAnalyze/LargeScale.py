import numpy as np

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
file_root = 'nolimitation/0.2-0.4/'
# file_root = 'nolimitation/0.1-0.2/'
# file_root = 'nolimitation/0.1-0.2/'
# file_root = 'nolimitation/0.1-0.2/'
# file_root = 'NewLS/0.2-0.4/'
# file_root = 'NewLS/0.6-1.0/'
folder_name = ['10', '20', '30', '40', '50', '60', '70', '80']
parent_folder = 0


def Theoretical():
    r_p = []
    r_e = []
    r_s = []
    for which_folder in range(len(folder_name)):
        pilots = []
        efficiency = []
        filename = file_root+'naive_%s.txt' % (folder_name[which_folder])
        with open(filename, 'r') as f:
            lines = f.readlines()
        for line in lines:
            l = line.strip('\n').split(' ')
            pilots.append(float(l[0]))
            efficiency.append(float(l[1]))
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
    s = ''
    for ele in r_p:
        s += ' %.2f' % ele
    print(s)
    s = ''
    for ele in r_e:
        s += ' %.4f' % ele
    print(s)

    s = ''
    for ele in r_s:
        s += ' %.2f' % ele
    print(s)



def Heuristic_1():
    r_p = []
    r_e = []
    r_ms = []
    r_packets = []
    for which_folder in range(len(folder_name)):
        pilots = []
        efficiency = []

        ms = []
        packets = []
        filename = file_root+'1/pilots_%s.txt' % folder_name[which_folder]
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            l = line.strip('\n').split(' ')
            pilots.append(int(l[0]))
            efficiency.append(float(l[1]))

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
    # print('Average pilots: %f' % (np.mean(pilots)))
    # print('Max pilots: %f' % max(pilots))
    # print('Average efficiency: %f' % (np.mean(efficiency)))
    # print('Average ratio between actial conf. and allowed conf.: %f' % np.mean(ratio_actual_allowed))
    # print('Real number of conf.: %f' % np.mean(real_conf))
    s = ''
    for ele in r_p:
        s += ' %.2f' % ele
    print(s)
    s = ''
    for ele in r_e:
        s += ' %.4f' % ele
    print(s)

    s = ''
    for ele in r_ms:
        s += ' %.2f' % ele
    print(s)

    s = ''
    for ele in r_packets:
        s += ' %d' % ele
    print(s)

def Heuristic_nolimitation():
    r_p = []
    r_e = []
    r_ms = []
    r_packets = []
    for which_folder in range(len(folder_name)):
        pilots = []
        efficiency = []
        real_conf = []
        ratio_actual_allowed = []

        ms = []
        packets = []
        filename = file_root+'COmax/pilots_%s.txt' % folder_name[which_folder]
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines:
            l = line.strip('\n').split(' ')
            pilots.append(int(l[0]))
            efficiency.append(float(l[1]))
            real_conf.append(int(l[3]))
            ratio_actual_allowed.append((int(l[3])) / int(l[2]))
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
    # print('Average pilots: %f' % (np.mean(pilots)))
    # print('Max pilots: %f' % max(pilots))
    # print('Average efficiency: %f' % (np.mean(efficiency)))
    # print('Average ratio between actial conf. and allowed conf.: %f' % np.mean(ratio_actual_allowed))
    # print('Real number of conf.: %f' % np.mean(real_conf))
    s = ''
    for ele in r_p:
        s += ' %.2f' % ele
    print(s)
    s = ''
    for ele in r_e:
        s += ' %.4f' % ele
    print(s)

    s = ''
    for ele in r_ms:
        s += ' %.2f' % ele
    print(s)

    s = ''
    for ele in r_packets:
        s += ' %d' % ele
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
