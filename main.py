# -*- coding: utf-8 -*- 

import sys
from datetime import datetime
import os
import re

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


# CREATE TABLE tableName(tableName CHAR(50) grade CHAR(3) sentence VARCHAR(100) department VARCHAR(20))
# INSERT into tableName values("minjoon","A+","hello world this is minjoon","SW")
# SELECT * FROM tableName WHERE name = "minjoon" AND grade = "A+" OR department = "SW"
# SELECT name grade FROM tableName

def err(errstr):
    print("Exception ocurred : ", errstr)
    exit()

def stringToBinary(string):
    return ' '.join(format(ord(c), 'b') for c in string)

def processQuery(query):
    print(query)
    # createTable("a","a")
    insertRow("a", "a")


def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        err("Error: Failed to create the directory.")


def createTable(tableName, args):
    tableName = "testTable"
    args = [("name", "CHAR(50)"), ("grade", "CHAR(3)"), ("sentence", "VARCHAR(100)"), ("department", "VARCHAR(20)")]

    # 메타메타 파일 열자

    try:
        meta = open("./meta.meta", 'r+')
    except:
        meta = open("./meta.meta", "w")
        meta.writelines("JOON DB meta.meta [" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "]")
        meta.writelines("\n")
        meta.writelines("\n")
        meta.flush()
        meta.close()
        meta = open("./meta.meta", 'r+')

    while True:
        readData = meta.readline()

        if readData != "":
            currTableName = readData.split(".meta")[0]
            print(currTableName)
            if tableName == currTableName:
                err("tableName already exists")
        else:
            break

    meta.writelines("\n" + tableName + ".meta ./" + tableName + "/")
    meta.flush()
    meta.close()

    # 테이블 폴더 만들자
    createDirectory("./" + tableName)
    # 메타 만들자

    meta = open("./" + tableName + "/" + tableName + ".meta", "a+")
    meta.writelines(tableName + ".meta [" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "]")
    meta.writelines("\n")
    meta.writelines("\n")

    for arg in args:
        meta.writelines("\n" + arg[0] + " " + arg[1])


def insertRow(tableName, args):
    tableName = "testTable"
    args = ["minjoon", "A+", "hello world this is minjoon", "SW"]

    # 메타에 쓰이는 3종 세트
    cols = []
    types = []
    sizes = []

    # 우선 테이블 메타 파일 열어야됌

    try:
        reader = open("./" + tableName + "/" + tableName + ".meta", "r")
    except:
        err(tableName + " meta not exists")

    while True:
        readData = reader.readline()

        if " CHAR(" in readData or " VARCHAR(" in readData:
            cols.append(readData.split(' ')[0])
            types.append(readData.split(' ')[1].split('(')[0])
            sizes.append(int(readData.split(' ')[1].split('(')[1].split(')')[0]))

        if readData == "":
            break

    print(cols)
    print(types)
    print(sizes)

    nullBitMap = []

    for i in range(len(args)):
        #empty string or null is preprocessed
        #convert to variable length record
        arg = args[i]

        if arg is None:
            nullBitMap.append(1)
        else:
            nullBitMap.append(0)


# file = open("sample.bin", "wb")
# file.write("hello world".encode())
# file.write(bytes([1,2,3,4,5]))
# file.close()


if __name__ != "__main__":
    exit()

# print("hello")

processQuery(sys.argv[1])

# data = re.sub(' ','',stringToBinary("hello world"))

