import numpy as np
import datetime

# 0: theoretical    1: SMT      2: Heuristic
which_category = 1
# which folder: 0: COmax    1: 1/2 COmax    2: 1
which_folder = 1


def Theoretical():
    lower = []
    upper = []
    lower_data = []
    efficiency = []

    success_data = []
    success_data_efficiency = []
    filename = ['Small_Scale/bound.txt',
                'Small_Scale/0.5COmax/bound.txt',
                'Small_Scale/1/bound.txt']
    with open(filename[which_folder], 'r') as f:
        lines = f.readlines()
    for line in lines:
        l = line.strip('\n').split(' ')
        lower.append(float(l[0]))
        lower_data.append(float(l[1]))
        upper.append(float(l[2]))
        efficiency.append(float(l[3]))

        if int(float(l[2])) <= 5:
            success_data.append(int(float(l[2])))
            success_data_efficiency.append(float(l[3]))

    print('Average pilots Lower: %f '% np.mean(lower))
    print('Average pilots without control Lower: %f' % np.mean(lower_data))
    print('Average pilots Upper: %f' % np.mean(upper))
    print('Efficiency (data) of Upper: %f' % np.mean(efficiency))
    print('Success rate: %f' % (len(success_data) / len(upper)))
    print('Efficiency (data) of success Upper: %f' % np.mean(success_data_efficiency))


def SMT():
    filename = 'old_withComax/Small_Scale/COmax/solvingtime.txt'
    with open(filename, 'r') as f:
        lines = f.readlines()
    timeinms = []
    for line in lines:
        print(line)
        l = line.strip('\n')
        d = 0
        if ',' not in l:
            print(l)
            ele = l.split(':')
            print(ele)
            h = int(ele[0])
            m = int(ele[1])
            mas = ele[2].split('.')
            s = int(mas[0])
            ms = int(mas[1])
            print(h, m, s, ms)
        else:
            l = l.split(' ')
            d = int(l[0])
            ele = l[2].split(':')
            print(ele)
            h = int(ele[0])
            m = int(ele[1])
            mas = ele[2].split('.')
            s = int(mas[0])
            ms = int(mas[1])
            print(h, m, s, ms)
        total = d * 24*60*60*1000 + h*60*60*1000 + m*60*1000 + s*1000 + ms/1000
        print(total)
        timeinms.append(total)

    print('Total average time consumption: %f' % np.mean(timeinms))



def Heuristic():
    pilots = []
    efficiency = []
    success_data = []
    success_data_efficiency = []
    filename = ['Small_Scale/COmax/pilots.txt',
                'Small_Scale/0.5COmax/pilots.txt',
                'Small_Scale/1/pilots.txt']
    with open(filename[which_folder], 'r') as f:
        lines = f.readlines()

    for line in lines:
        l = line.strip('\n').split(' ')
        pilots.append(int(l[0]))
        efficiency.append(float(l[1]))
        if int(l[0]) <= 5:
            success_data.append(int(l[0]))
            success_data_efficiency.append(float(l[1]))

    print('Success rate: %f' % (len(success_data) / len(pilots)))
    print('Average pilots: %f' % (np.mean(success_data)))
    print('Average efficiency: %f' % (np.mean(success_data_efficiency)))


if which_category == 0:
    Theoretical()
elif which_category == 1:
    SMT()
elif which_category == 2:
    Heuristic()
