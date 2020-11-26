from bs4 import BeautifulSoup

instructions = []

def parse_td(table_num, row_num, data_num, data):
    


def parse_tr(table_num, row_num, row):
    tds = row.find_all("td")
    for i, td in enumerate(tds):
        parse_td(table_num, row_num, i, td)


def parse_table(table_num, table):
    trs = table.find_all("tr")
    for i, tr in enumerate(trs):
        parse_tr(table_num, i, tr)
    

file = open("z80.html")
html = file.read()
soup = BeautifulSoup(html, "html.parser")
tables = soup.find_all("table")

for i, table in enumerate(tables):
    parse_table(i, table)
