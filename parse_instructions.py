from bs4 import BeautifulSoup

instructions = []

instruction_list = []

instruction_set = set()

INSTRUCTION_TEMPLATE = 'Instruction(opcode="{}", instruction_base="{}", left_arg="{}", right_arg="{}", size="{}", time="{}", flags="{}", text="{}", desc="{}"),'

class Instruction:
    
    def __init__(self, opcode, text, size, time, flags, desc, instruction_base, left_arg=None, right_arg=None):
        self.opcode = opcode
        self.text = text
        self.size = size
        self.time = time
        self.flags = flags
        self.desc = desc
        self.instruction_base = instruction_base
        self.left_arg = left_arg
        self.right_arg = right_arg


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
    instruction[4] = str(instruction[4])
    if instruction[0] == 1:
        instruction[4] = "ED" + instruction[4]
    elif instruction[0] == 2:
        instruction[4] = "CB" + instruction[4]
    elif instruction[0] == 3:
        instruction[4] = "DD" + instruction[4]
    elif instruction[0] == 4:
        instruction[4] = "DDCB" + instruction[4]
    elif instruction[0] == 5:
        instruction[4] = "FD" + instruction[4]
    elif instruction[0] == 6:
        instruction[4] = "FDCB" + instruction[4]
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
    instruction_set.add(instruction_base)
    #print(new_instruction)

instruction_set = set()
for instruction in instruction_list:
    #if instruction.text[:2] == "ld":
        #print(instruction.text, instruction.size, instruction.time, instruction.flags, instruction.desc, instruction.instruction_base)
    '''
    print(INSTRUCTION_TEMPLATE.format(
            instruction.opcode, instruction.instruction_base, instruction.left_arg, instruction.right_arg,
            instruction.size, instruction.time, instruction.flags, instruction.text, instruction.desc))
    '''
    if instruction.instruction_base[:3] == "xor":
        instruction_set.add((instruction.text, instruction.desc))

for e in instruction_set:
    print(e[0])

#for instruction in instruction_set:
#    print(instruction)

#print(len(instruction_set))

