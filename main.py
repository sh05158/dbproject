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
    if "CREATE TABLE " in query.upper():
        tableName = query.split("CREATE TABLE ")[1].split("(")[0].strip()
        args = []
        argsArr = query[query.find("(")+1:].split(") ")

        for arg in argsArr:
            try:
                argName = arg.split(" ")[0]
                argPref = arg.split(" ")[1]
                if argPref[-1] != ")":
                    argPref = argPref + ")"
                if argPref[-1] == ")" and argPref[-2] == ")":
                    argPref = argPref[:-1]

                args.append((argName,argPref))
            except:
                print('',end='')

        print( createTable(tableName, args) )

    elif "INSERT INTO" in query.upper():
        tableName = query.split("INSERT INTO ")[1].split("VALUES")[0].strip()
        args = query.split("VALUES")[1].strip().split("(")[1].split(")")[0].split(",")
        newArgs = []
        for arg in args:
            arg = arg.strip('"')
            newArgs.append(arg)

        print( insertRow(tableName, args) )

    elif "SELECT " in query.upper():
        tableName = query.split("FROM ")[1].split("WHERE")[0].strip()
        selectCols = query.split("SELECT")[1].split("FROM")[0].strip().split(" ")
        try:
            conds = query.split("WHERE")[1].strip().split("AND")
        except:
            conds = []

        condsArr = []

        for cond in conds:
            colName = cond.split("=")[0].strip()
            value = cond.split("=")[1].strip().strip('"')
            condsArr.append((colName,value))

        result = ( selectTable(tableName,selectCols, selectCols[0]=="*", condsArr) )

        print( len(result),"Rows Selected." )

        if len(result) <= 0:
            return

        cols = result[0].keys()
        for col in cols:
            print("%40s " %(col), end='')
        print("")
        
        for col in cols:
            print("-------------------------------------------",end="")
        print("")

        for res in result:
            for col in cols:
                print("%40s " %(res[col]), end='')
            print("")



def createDirectory(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        err("Error: Failed to create the directory.")


def createTable(tableName, args):

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

    return tableName+" is created successfully."


def insertRow(tableName, args):

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

    nullBitMap = ""
    nullBitMapArr = []
    record = ""
    varcharOffset = 1  #맨 앞에 null bitmap 이 있기 때문에

    varcharOffset += len(list(filter(lambda x: x == "VARCHAR", types))) * 4
    varcharOffset += sum( [x["sizes"] for x in colData if x["types"] == "CHAR"] )

    for i in range(len(args)):
        #empty string or null is preprocessed
        #convert to variable length record
        arg = args[i]

        if len(arg) > sizes[i]:
            err("column "+cols[i]+" exceed length limit "+str(sizes[i])+"  ("+str(len(arg))+")")

        if arg is None or arg == "NULL":
            nullBitMap += "1"
            arg = ''
            args[i] = ''
        else:
            nullBitMap += "0"

        if types[i] == "CHAR":
            record += rpad(arg,sizes[i],' ')
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


    nullBitMap = rpad(nullBitMap,8,'0')


    nullDecimal = chr(int(nullBitMap,2)+1)

    
    record = nullDecimal + record

    #이제 슬롯을 찾아서 레코드를 넣을거임 

    slotCurr = 0
    while True:
        if insertSlot(tableName, slotCurr, record) == 1: #성공했을 시 루프 빠져나간다..
            break
        slotCurr += 1

    return tableName+ " inserted 1 row successfully."

def checkSlot(tableName, slotNum):
    return exists("./" + tableName + "/slot" + lpad(slotNum,3,'0') + ".bin")

def createSlot(tableName, slotNum):
    slot = open("./" + tableName + "/slot" + lpad(slotNum,3,'0') + ".bin", "wb+")

    slot.seek(0)
    slot.write(lpad("\0",4000,'\0').encode())

    slot.seek(0)
    slot.write(struct.pack('b',0))

    slot.flush()
    slot.close()


def selectTable(tableName, columns, selectAll=True, conditions=[]):
    returnData = []

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

    slotNum = 0

    while True:
        try:
            slot = open("./" + tableName + "/slot" + lpad(slotNum,3,'0') + ".bin", "rb")
        except:
            break

        recordPointer = -1
        i = 1
        while i < SLOT_SIZE-1:
            tempReturnCol = {}

            slot.seek(i)
            readData = slot.read(2)
            currRecordPointer = int(struct.unpack("H",readData)[0])+1
            nextRecordPointer = -1

            if i < SLOT_SIZE-3:
                slot.seek(i+2)
                readData2 = slot.read(2)
                nextRecordPointer = int(struct.unpack("H",readData2)[0])

            if nextRecordPointer == 0:
                nextRecordPointer = SLOT_SIZE
            
            if currRecordPointer <= 1:
                break
            
            slot.seek(currRecordPointer-1)
            buf = slot.read(abs(nextRecordPointer-currRecordPointer))
            temp = abs(nextRecordPointer-currRecordPointer)
            columnData = str(buf.decode())
            nullBitMap = lpad(str(bin(buf[0]-1)).split('0b')[1],8,'0')
            columnIter = 1

            for idx, type in enumerate(types):
                if cols[idx] not in columns and selectAll == False:
                    if type == "CHAR":
                        columnIter += sizes[idx]
                    elif type == "VARCHAR":
                        columnIter += 4
                    #생략해도 되는 컬럼.. 값 리턴 안해줘도 된다.
                    continue
                else:
                    #리턴 데이터에 넣어 줘야되는 컬럼 
                    if type == "CHAR":
                        if nullBitMap[idx] == "1":
                            tempReturnCol[cols[idx]]="NULL"
                        else:
                            tempReturnCol[cols[idx]]=columnData[columnIter:columnIter+sizes[idx]]
                            columnIter += sizes[idx]
                    elif type == "VARCHAR":
                        if nullBitMap[idx] == "1":
                            tempReturnCol[cols[idx]]="NULL"
                            columnIter += 4
                        else:
                            startIdx = int(columnData[columnIter:columnIter+2])
                            size = int(columnData[columnIter+2:columnIter+4])
                            tempReturnCol[cols[idx]]=columnData[startIdx:startIdx+size]
                            columnIter += 4

            flag = False

            for cond in conditions:
                # print(str(cond)+"@"+tempReturnCol[cond[0]]+"@"+cond[1]+"@" )
                if tempReturnCol[cond[0]].rstrip() != cond[1]:
                    #조건 하나라도 안맞으면 안넣고 continue
                    flag = True
                    break

            if flag == False:
                returnData.append(tempReturnCol)
            i += 2
        slotNum += 1

    return returnData


#특정 슬롯에 레코드를 삽입하는 함수, 공간이 부족해서 실패하면 -1리턴 
def insertSlot(tableName, slotNum, record): 
    if checkSlot(tableName, slotNum) == False:
        #없으면 만들자
        createSlot(tableName, slotNum)

    try:
        slot = open("./" + tableName + "/slot" + lpad(slotNum,3,'0') + ".bin", "rb+")
    except:
        err("table "+ tableName+ " slot "+slotNum +" not exists ")

    #빈공간 찾아야됌

    slot.seek(0)
    count = slot.read(1)
    count = int(struct.unpack('b',count)[0])


    emptyPointer = -1
    slot.seek(SLOT_SIZE) ##마지막으로 커서를 옮겨서 한 바이트씩 읽어서 \0이 아닐때까지 읽는다 

    for i in range(0,SLOT_SIZE-len(record)-2-1-count*2): #레코드 포인터가 2바이트라서 2를 추가적으로 뺐다( 레코드 포인터의 여유 공간까지 고려 )
        slot.seek(SLOT_SIZE-i)

        readData = slot.read(1)

        if readData == b'\x00':
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
        slot.seek(i)
        readData = slot.read(2)
        data = int(struct.unpack("H",readData)[0])

        if data == 0:
            recordPointer = i
            break
        i += 2
    

    if recordPointer == -1:
        err("슬롯 공간은 있는데 레코드 포인터가 없는 말도 안되는 경우")
    slot.seek(recordPointer)
    slot.write( struct.pack('H',startPoint)  )


    #삽입에 성공했으므로 슬롯 헤더에 레코드 갯수를 1 올려줘야 됌 .
    slot.seek(0)
    count = slot.read(1)
    count = int(struct.unpack('b',count)[0])

    slot.seek(0)
    slot.write(struct.pack('b',count+1))

    slot.close()
    
    return 1
    
if __name__ != "__main__":
    exit()

queryString = ""
for idx, arg in enumerate(sys.argv):
    if idx == 0:
        continue
    queryString += arg+" "

processQuery(queryString)