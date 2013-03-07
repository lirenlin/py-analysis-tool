#!/usr/bin/env python

import cPickle as pickle
import os
import glob

import barPlot

def readPickle(fileName):
    barPlot.newFigure()

    file = open(fileName)
    dataList = pickle.load(file)
    num = 0;
    for barData in dataList:
        barPlot.drawBar(barData, num)
        num += 1

    file.close
    barPlot.done()
    barPlot.showFigure()

def readPickle_1(fileName):
    file = open(fileName)
    dataList = pickle.load(file)
    for file, data in dataList:
        print "*"*20
        print "%s:"%(file)
        for item in data:
                print item
    file.close()

if __name__ == "__main__":
    readPickle("analysisCache.p")
    readPickle_1("analysisCache-1.p")

