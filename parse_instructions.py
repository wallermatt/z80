from bs4 import BeautifulSoup

instructions = []

instruction_list = []

class Instruction:
    
    def __init__(self, opcode, text, size, time, flags, desc, instruction_base, left=None, right=None):
        self.opcode = opcode
        self.text = text
        self.size = size
        self.time = time
        self.flags = flags
        self.desc = desc
        self.instruction_base = instruction_base
        self.left = left
        self.right = right


    def __str__(self):
        return "{} {} {} {}".format(self.opcode, self.instruction_base, self.left, self.right)

def parse_td(table_num, row_num, data_num, data):
    if data.has_attr("axis"):
        opcode = (row_num - 1) * 16 + data_num
        instructions.append([table_num, row_num, data_num, hex(opcode), opcode, data.contents[0], data["axis"]])


def parse_tr(table_num, row_num, row):
    tds = row.find_all("td", {})
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


for instruction in instructions:
    if instruction[0] > 0:
        break
    #print(instruction)
    instruction_text = instruction[5]
    components = instruction_text.split(" ")
    instruction_base = components[0]
    left_arg = None
    right_arg = None
    if len(components) > 1:
        args = components[1].split(",")
        left_arg = args[0]
        if len(args) > 1:
            right_arg = args[1]

    extra_info = instruction[6].split("|")
    flags = extra_info[0]
    size = extra_info[1]
    time = extra_info[2]
    desc = extra_info[3]

    new_instruction = Instruction(instruction[4], instruction[5], size, time, flags, desc, instruction_base, left_arg, right_arg)
    instruction_list.append(new_instruction)
    print(new_instruction)

for instruction in instruction_list:
    print(instruction.text, instruction.size, instruction.time, instruction.flags, instruction.desc)

