# -*- coding: utf-8 -*- 

import binascii
import struct
import sys
from datetime import datetime
import os
from os.path import exists
import re

from bitarray import bitarray

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

SLOT_SIZE = 4000

# CREATE TABLE tableName(tableName CHAR(50) grade CHAR(3) sentence VARCHAR(100) department VARCHAR(20))
# INSERT into tableName values("minjoon","A+","hello world this is minjoon","SW")
# SELECT * FROM tableName WHERE name = "minjoon" AND grade = "A+" OR department = "SW"
# SELECT name grade FROM tableName

def err(errstr):
    print("Exception ocurred : ", errstr)
    exit()

def lpad(i, width, fillchar='0'):
    """입력된 숫자 또는 문자열 왼쪽에 fillchar 문자로 패딩"""
    return str(i).rjust(width, fillchar)

def rpad(i, width, fillchar='0'):
    """입력된 숫자 또는 문자열 오른쪽에 fillchar 문자로 패딩"""
    return str(i).ljust(width, fillchar)

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
    colData = []
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

            temp = {}
            temp["cols"] = readData.split(' ')[0]
            temp["types"] = readData.split(' ')[1].split('(')[0]
            temp["sizes"] = int(readData.split(' ')[1].split('(')[1].split(')')[0])

            colData.append(temp)
        if readData == "":
            break

    print(cols)
    print(types)
    print(sizes)

    nullBitMap = ""
    nullBitMapArr = []
    record = ""
    varcharOffset = 1  #맨 앞에 null bitmap 이 있기 때문에

    varcharOffset += len(list(filter(lambda x: x == "VARCHAR", types))) * 4
    varcharOffset += sum( [x["sizes"] for x in colData if x["types"] == "CHAR"] )

    print("offset:",varcharOffset)

    for i in range(len(args)):
        #empty string or null is preprocessed
        #convert to variable length record
        arg = args[i]

        if arg is None:
            nullBitMap += "0"
        else:
            nullBitMap += "1"

        if types[i] == "CHAR":
            record += rpad(arg,sizes[i],'0')
        elif types[i] == "VARCHAR":
            record += str(varcharOffset)+lpad(str(len(arg)),2,'0')
            varcharOffset += len(arg)

    for i in range(len(args)):
        arg = args[i]
        if types[i] == "VARCHAR":
            record += arg

    # args = ["minjoon", "A+", "hello world this is mslacinjoon", "SW"]
    for i in range(len(nullBitMap)):
        if nullBitMap[i] == "0":
            nullBitMapArr.append(0)
        else:
            nullBitMapArr.append(1)


    print("null bit map ",bytes(nullBitMapArr))

    nullDecimal = chr(int(nullBitMap,2))
    

    
    record = nullDecimal + record

    #이제 슬롯을 찾아서 레코드를 넣을거임 

    slotCurr = 0
    while True:
        if insertSlot(tableName, slotCurr, record) == 1: #성공했을 시 루프 빠져나간다..
            break
        print(slotCurr)
        slotCurr += 1


def readSlot(tableName):
    tableName = "testTable"
    args = ["minjoon", "A+", "hello world this is minjoon", "SW"]

    # 메타에 쓰이는 3종 세트
    cols = []
    types = []
    sizes = []
    colData = []
    # 우선 테이블 메타 파일 열어야됌

    try:
        reader = open("./" + tableName + "/" + tableName + ".meta", "r")
    except:
        err(tableName + " meta not exists")

def checkSlot(tableName, slotNum):
    # try:
    #     slot = open("./" + tableName + "/slot" + lpad(slotNum,3,'0') + ".bin", "r")
    # except:
    #     return False
    #     err("table "+ tableName+ " slot "+slotNum +" not exists ")
    # slot.close()
    # return True
    return exists("./" + tableName + "/slot" + lpad(slotNum,3,'0') + ".bin")

def createSlot(tableName, slotNum):
    tableName="testTable"
    # slotNum=0
    
    slot = open("./" + tableName + "/slot" + lpad(slotNum,3,'0') + ".bin", "wb+")

    # slot.write(lpad("",4000,'0').encode())
    slot.seek(0)
    slot.write(lpad("\0",4000,'\0').encode())

    slot.seek(0)
    slot.write(struct.pack('b',0))

    slot.flush()
    slot.close()

    print("creat slot "+tableName+"/ "+str(slotNum))

def selectTable(tableName):
    tableName = "testTable"
    args = ["minjoon", "A+", "hello world this is minjoon", "SW"]

    # 메타에 쓰이는 3종 세트
    cols = []
    types = []
    sizes = []
    colData = []
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

            temp = {}
            temp["cols"] = readData.split(' ')[0]
            temp["types"] = readData.split(' ')[1].split('(')[0]
            temp["sizes"] = int(readData.split(' ')[1].split('(')[1].split(')')[0])

            colData.append(temp)
        if readData == "":
            break

    print(cols)
    print(types)
    print(sizes)


#특정 슬롯에 레코드를 삽입하는 함수, 공간이 부족해서 실패하면 -1리턴 
def insertSlot(tableName, slotNum, record):
    tableName="testTable"
    # slotNum=0
    
    if checkSlot(tableName, slotNum) == False:
        #없으면 만들자
        print("없음")
        createSlot(tableName, slotNum)
    else:
        print("있음")


    try:
        slot = open("./" + tableName + "/slot" + lpad(slotNum,3,'0') + ".bin", "rb+")
    except:
        err("table "+ tableName+ " slot "+slotNum +" not exists ")

    #빈공간 찾아야됌
    
    # for i in range(0,SLOT_SIZE):
    #     slot.seek(i)

    #     readData = slot.read(1)

    #     print(readData.decode())
    
    # print("끝")
    # slot.flush()
    # slot.close()
    # return 1

    slot.seek(0)
    count = slot.read(1)
    count = int(struct.unpack('b',count)[0])


    emptyPointer = -1
    slot.seek(SLOT_SIZE-1) ##마지막으로 커서를 옮겨서 한 바이트씩 읽어서 \0이 아닐때까지 읽는다 

    for i in range(0,SLOT_SIZE-len(record)-2-1-count*2): #레코드 포인터가 2바이트라서 2를 추가적으로 뺐다( 레코드 포인터의 여유 공간까지 고려 )
        slot.seek(SLOT_SIZE-1-i)

        readData = slot.read(1)
        # print(str(i)+"readData @@"+readData.decode()+"@@")
        if readData.decode() == '\x00':
            # print("찾음!"+str(SLOT_SIZE-1-i))
            emptyPointer = SLOT_SIZE-i
            if i != 0:
                emptyPointer += 1
            break
    
    if emptyPointer == -1:
        slot.close()
        return -1  # 해당 슬롯에 빈공간이 없어서 -1리턴

    startPoint = emptyPointer-len(record)
    slot.seek(startPoint)
    slot.write(record.encode())

    slot.seek(0)

    recordPointer = -1
    i = 1
    while i < SLOT_SIZE-1:
    # for i in range(1,SLOT_SIZE):
        slot.seek(i)
        readData = slot.read(2)
        data = int(struct.unpack("H",readData)[0])
        # print("seek "+str(i) +"@@"+str(readData)+"@@")
        
        if data == 0:
            print("찾음22!")
            recordPointer = i
            break
        i += 2
    
    print("레코드 포인터 "+str(recordPointer))

    if recordPointer == -1:
        err("슬롯 공간은 있는데 레코드 포인터가 없는 말도 안되는 경우")
    # print("startpoint : "+bin(startPoint))
    # print(bitarray(bin(startPoint)[2:]).tobytes())
    # print(binify(startPoint))
    slot.seek(recordPointer)
    # slot.write( binify(startPoint) )
    slot.write( struct.pack('H',startPoint)  )


    #삽입에 성공했으므로 슬롯 헤더에 레코드 갯수를 1 올려줘야 됌 .
    slot.seek(0)
    count = slot.read(1)
    count = int(struct.unpack('b',count)[0])

    slot.seek(0)
    slot.write(struct.pack('b',count+1))

    slot.close()
    
    return 1
    

def binify(x):
    h = hex(x)[2:].rstrip('L')
    return binascii.unhexlify('0'*(4-len(h))+h)
    

# file = open("sample.bin", "wb")
# file.write("hello world".encode())
# file.write(bytes([33,34]))
# file.close()


if __name__ != "__main__":
    exit()

# createSlot("test",1)

# print("hello")

processQuery(sys.argv[1])

# data = re.sub(' ','',stringToBinary("hello world"))

