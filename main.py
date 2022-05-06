import sys
from datetime import datetime
#CREATE TABLE tableName(tableName CHAR(50) grade CHAR(3) sentence VARCHAR(100) department VARCHAR(20))
#INSERT into tableName values("minjoon","A+","hello world this is minjoon","SW")
#SELECT * FROM tableName WHERE name = "minjoon" AND grade = "A+" OR department = "SW"
#SELECT name grade FROM tableName

def error(errstr):
    print("Exception ocurred : ",errstr)

def processQuery(query):
    print(query)
    createTable("a","a")
    
def createTable(tableName, args):
    tableName = "testTable"
    args = [("name","CHAR(50)"),("grade","CHAR(3)"),("sentence","VARCHAR(100)"),("department","VARCHAR(20)")]
    
    #메타 파일 열자
    
    try:
        meta = open("./meta.meta",'r')
    except:
        meta = open("./meta.meta","w")
        meta.writelines("JOON DB meta.meta ["+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"]")
        meta.writelines("\n")
        meta.writelines("\n")
        meta.flush()
        meta.close()
        meta = open("./meta.meta",'r')

    print(meta.read())
    
if __name__ != "__main__":
    exit()
    
    
print("hello")

processQuery(sys.argv[1])