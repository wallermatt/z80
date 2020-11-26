from bs4 import BeautifulSoup

file = open("z80.html")
html = file.read()
soup = BeautifulSoup(html, "html.parser")

#print(soup.prettify())

table1 = soup.find(id="table1")
#print(table1)

tables = soup.find_all("table")

#for table in tables:

tds = soup.find_all("td")
print(len(tds))

for i, td in enumerate(tds):
    print(td)
    if i == 15:
        break