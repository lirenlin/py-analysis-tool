#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

if __name__ != "__main__":
    xLabels = list()
    width = 0.35
    N = 0
    legend = list()

    fig = None
    ax = None

    color = ('LightCoral', 'DeepPink', 'Orange', 'Yellow', 
            'Lime', 'Olive', 'Peru', 'Cyan', 'RoyaBlue',
            'Magenta', 'DimGray', 'Black')

class BarData:
    "class to store the data to draw one vertical bar"
    def __init__(self, label, dataList):
        "do normalization"
        name, num = zip(*dataList)
        sumUp = sum(num)
        normalize = [round(float(y)/sumUp*100, 2) for y in num]

        self.label = label
        self.dataList = zip(name, normalize)

    def __str__(self):
        str = self.label + '\n'
        for name, percentage in self.dataList: 
            str += "%-10s: %.2f%%\n"%(name, percentage)
        return str

def newFigure():
    global fig, ax
    fig = plt.figure()
    ax = fig.add_subplot(111)

def drawBar( barData, start):

    global N, legend, color
    legend = list()

    N = N + 1
    label = barData.label
    xLabels.append(label)
    dataList = barData.dataList


    Last = 0
    for i in range(len(dataList)):
        name, percentage = dataList[i]
        rects = ax.bar(start, percentage, width, color=color[i], bottom=Last)

        rect = rects[0]
        if (name, rect) not in legend:
            legend.append((name, rect))
        height = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 0.4*height+Last, '%.2f'%height,
                ha='center', va='bottom')
        Last += percentage


def done(yLabel="Percentage", title="Instruction distribution"):
    ax.set_ylabel(yLabel)
    ax.set_title(title)

    ax.set_xticklabels(xLabels)
    for label in ax.get_xticklabels():
        label.set_rotation(-60)

    ind = np.arange(N+1)
    ax.set_xticks(ind + width/2)

    names, rects = zip(*legend)
    ax.legend(rects, names)

    plt.ylim((0, 110))
    plt.yticks(np.arange(0,110,10))

def showFigure():
    plt.show()

def saveFigure(name):
    plt.savefig(name)

