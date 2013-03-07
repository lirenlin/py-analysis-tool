#!/usr/bin/env python

from optparse import OptionParser
import os
import glob
import collections
import cPickle as pickle

import barPlot


def parseOptions():
    "parse the CLI options"
    parser = OptionParser()
    parser.add_option("-d", "--directory", action="store", type="string",
            dest="dirName", help="the directory of the folder")
    parser.add_option("-s", "--summery", action="store_true", default=False,
            dest="summery", help="generate summery report")
    parser.add_option("-c", "--chance", action="store_true", default=False,
            dest="chance", help="generate chance analysis report")
    parser.add_option("-p", "--pattern", action="store", default="asmDump*",
            dest="fileName", help="the file name")

    (options, args) = parser.parse_args()
    success = True

    dirName = options.dirName
    fileName = options.fileName
    summery = options.summery
    chance = options.chance

    if not (dirName):
        parser.print_help()
        success = False

    return (success, dirName, fileName, summery, chance)

# instruction classification
alu_insn = ( "CMOV", "ALU_OP_MOVE", "ALU_OP_ADD" , "ALU_OP_SUB",
        "ALU_OP_RSUB", "ALU_OP_NEG", "ALU_OP_MUL")

bit_insn = ( "ALU_OP_AND", "ALU_OP_OR", "ALU_OP_XOR", "ALU_OP_INV",
        "ALU_OP_SLL", "ALU_OP_SRL", "ALU_OP_SRA", "ALU_OP_SXT8",
        "ALU_OP_SXT16", "ALU_OP_ZXT16")

logic_insn = ( "CMP_OP_EQ", "CMP_OP_NE", "CMP_OP_LT", "CMP_OP_LE",
        "CMP_OP_LTU", "CMP_OP_LEU", "CMP_OP_GT", "CMP_OP_GE",
        "CMP_OP_GTU", "CMP_OP_GEU")

control_insn = ( "JMPI_UNCOND", "JMPI_COND", "JMPR_UNCOND",
        "CALLR_UNCOND", "JMPIL_UNCOND", "JMPIL_COND", "CALLIL_UNCOND")

mem_insn = ( "LDST_LW", "LDST_LH", "LDST_LHU", "LDST_LB",
        "LDST_LBU", "LDST_SW", "LDST_SH", "LDST_SB")

nop_insn = ( "NOP" ),

insn_set = alu_insn + bit_insn + logic_insn + \
        control_insn + mem_insn + nop_insn

insn_class = { "alu_insn": alu_insn, "bit_insn": bit_insn,
        "logic_insn": logic_insn, "control_insn": control_insn,
        "mem_insn": mem_insn, "nop_insn": nop_insn}

#insn_class = ( "alu_insn", "bit_insn", "logic_insn",
#        "control_insn", "mem_insn", "nop_insn")

#print len(alu_insn + bit_insn + mem_insn + nop_insn + logic_insn + control_insn)

def initDict(insn_set):
    "initial an empty dictionary using given keys"
    collectDict = dict()
    for insn in insn_set:
        collectDict[insn] = 0
    return collectDict

def generateSummery(classDict, collectDict):
    for key in collectDict.keys():
        if key in alu_insn:
            classDict["alu_insn"] += collectDict[key]
        elif key in bit_insn:
            classDict["bit_insn"] += collectDict[key]
        elif key in logic_insn:
            classDict["logic_insn"] += collectDict[key]
        elif key in control_insn:
            classDict["control_insn"] += collectDict[key]
        elif key in mem_insn:
            classDict["mem_insn"] += collectDict[key]
        elif key in nop_insn:
            classDict["nop_insn"] += collectDict[key]
        else:
            print "Skip unknown instruction {0}".format(key)

    return classDict

class Record:
    "store one record"
    def __init__(self, start='NONE', end='NONE', len=0):
        self.start = start
        self.end = end
        self.len= len

    def __eq__(self, other):
        if (self.start == other.start) and  (self.end == other.end):
            return True

    def __str__(self):
        return "%-12s-->%12s: %d" % (self.start, self.end, self.len)

    def direction(self):
        return "%-12s-->%12s" % (self.start, self.end)

    def clear(self):
        self.start = 'NONE'
        self.end = 'NONE'
        self.len = 0

def chanceAnalysis(maxGap, file, rule):
    '''analysis the time some unit is free
    i.e. chance that can use this unit for other purpose '''
    count = 0
    flip = False
    record = Record()
    aggregate = dict()


    for line in file:
        word = line.rstrip(os.linesep)
        count += 1
        if word in insn_set:
            for key in insn_class.keys():
                if word in insn_class[key]:
                    if record.start == 'NONE':
                        record.start = key
                        record.len = 1
                    elif record.start == key:
                        record.len += 1
                    else:
                        record.end = key
                        label = record.__str__()
                        if label in aggregate:
                            aggregate[label] += 1
                        else:
                            aggregate[label] = 1

                        record = Record(start=key, len=1)
                    break

    sortedList = sorted(aggregate.items())
    return sortedList

def collectInfo(file):
    dumpList = list()

    collectDict = initDict(insn_set)
    # collect the statistics
    for line in file:
        word = line.rstrip(os.linesep)
        if word in collectDict:
            collectDict[word] += 1
        else:
            print "Skip unknown instruction {0}".format(word)

    classDict = initDict(insn_class)
    classDict = generateSummery(classDict, collectDict)

    total = sum(classDict.values())
    print "%-14s:Total cycles: %d" % ("Summery", total)
    print "*"*20

    dataList = classDict.items()
    sorted_by_second = sorted(dataList, key=lambda tup: tup[1], reverse=True)

    return sorted_by_second

if __name__ == "__main__":

    (success, dirName, fileName, summery, chance) = parseOptions()
    if not success:
        exit()

    if not (os.path.exists(dirName)):
        error = "folder is %s not found\n"%(dirName)
        exit()

    dumpList1 = list()
    dumpList2 = list()

    for root, dirnames, filenames in os.walk(dirName):
        for filePath in glob.glob(os.path.join(root, fileName)):
            file = open(filePath)
            dir = os.path.dirname(filePath)
            folder = dir.split(os.sep)[-1]
            print folder

            if chance:
                dataList1 = chanceAnalysis(3, file, 0)
                dumpList1.append((folder, dataList1))
                file.seek(0)
            if summery:
                dataList2 = collectInfo(file)
                barData = barPlot.BarData(folder, dataList2)
                dumpList2.append(barData)

            file.close()

    if chance:
        pickle.dump(dumpList1, open("analysisCache-1.p", "wb"))
    if summery:
        pickle.dump(dumpList2, open("analysisCache.p", "wb"))
