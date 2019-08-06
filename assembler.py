#!/usr/bin/python

import sys
import re
import math

LocCtr = 0

nostart = None

SymTab = {}

addressList = []
size_end = 0

END = None
# [size, OpCode, arguments]

OpTab = {'ADD':[3,'18',1],'ADDF':[3,'58',1],'ADDR':[2,'90',2],'AND':[3,'40',1],'CLEAR':[2,'B4',1],
    'COMP':[3,'28',1],'COMPF':[3,'88',1],'COMPR':[2,'A0',2],'DIV':[3,'24',1],'DIVF':[3,'64',1],
    'DIVR':[2,'9C',2],'FIX':[1,'C4',0],'FLOAT':[1,'C0',0],'HIO':[1,'F4',0],'J':[3,'3C',1],
    'JEQ':[3,'30',1],'JGT':[3,'34',1],'JLT':[3,'38',1],'JSUB':[3,'48',1],'LDA':[3,'00',1],
    'LDB':[3,'68',1],'LDCH':[3,'50',1],'LDF':[3,'70',1],'LDL':[3,'08',1],'LDS':[3,'6C',1],
    'LDT':[3,'74',1],'LDX':[3,'04',1],'LPS':[3,'D0',1],'MUL':[3,'20',1],'MULF':[3,'60',1],
    'MULR':[2,'98',2],'NORM':[1,'C8',0],'OR':[3,'44',1],'RD':[3,'D8',1],'RMO':[2,'AC',2],
    'RSUB':[3,'4C',0],'SHIFTL':[2,'A4',2],'SHIFTR':[2,'A8',2],'SIO':[1,'F0',0],'SSK':[3,'EC',1],
    'STA':[3,'0C',1],'STB':[3,'78',1],'STCH':[3,'54',1],'STF':[3,'80',1],'STI':[3,'D4',1],
    'STL':[3,'14',1],'STS':[3,'7C',1],'STSW':[3,'E8',1],'STT':[3,'84',1],'STX':[3,'10',1],
    'SUB':[3,'1C',1],'SUBF':[3,'5C',1],'SUBR':[2,'94',2],'SVC':[2,'B0',1],'TD':[3,'E0',1],
    'TIO':[1,'F8',0],'TIX':[3,'2C',1],'TIXR':[2,'B8',1],'WD':[3,'DC',1],
    'A':[0], 'X': [1], 'L': [2], 'B': [3], 'S': [4], 'T': [5], 'F': [6], 'PC': [8], 'SW': [9]
    }


# figure tabs out
def RemoveTabsandNewline(line):
    t_line = list(line)
    if '\n' in t_line:
        t_line.remove('\n')

    t_line = ["" if x == '\r' else x for x in t_line]
    count = 0
    # CITE: List comprehension from
    # https://stackoverflow.com/questions/2582138/finding-and-replacing
    t_line = [" " if x == '\t' else x for x in t_line]
    # while '\t' in t_line:
    #     t_line.remove('\t')
    #     count += 1

    new = ""
    for x in t_line:
        if count == 40:
            break
        new += x
        count += 1
    t_line = new

    return t_line


    # DO THIS PROPERLY
def CheckFOrComment(line):
    mylist = list(line)
    while " " in mylist:
        mylist.remove(" ")

    if mylist[0] == ".":
        return True
    else:
        return False


def HexLocCounter():
    global LocCtr
    H_locCtr = hex(LocCtr)
    H_locCtr = H_locCtr[2:]
    while len(H_locCtr) < 6:
        H_locCtr = '0' + H_locCtr
    return H_locCtr


def OutputSymTab():

    # print (SymTab.keys())
    # CITE: Helped Nonso with sorted function
    for i in sorted(SymTab.keys()):
        g = i
        g = g + ":"
        print (" "),
        print (g),
        print (SymTab[i].upper())


def OutputPass2(addressList, outfile):
    # CITE: Helped Nonso with this function
    print addressList
    addressList = "".join(addressList)
    outfile.write(addressList[:7])

    addressList = addressList[7:]

    addressList = ["48" if x == "H" else x for x in addressList]
    addressList = ["54" if x == "T" else x for x in addressList]
    addressList = ["45" if x == "E" else x for x in addressList]

    addressList = list("".join(addressList))

    outputchar = ""

    for i in addressList:
        outputchar += i
        if len(outputchar) == 2:
            outfile.write(chr(int(outputchar, 16)))
            outputchar = ""



def main():
    global LocCtr
    global END
    global addressList
    global nostart
    base = None

    if len(sys.argv) < 2:
        print "Usage: demo <file>"
        exit(1)

    filename = sys.argv[1]

    filename2 = sys.argv[2]

    infile = open(filename, "r")

    outfile = open(filename2,"w+")

    line = infile.readline()

    # Code to ensure lenght less than or equal to 40 for a line. Tabs nothandle
    # RemoveTabsandNewline(line)
    # line = RemoveTabsandNewline(line)
    # lineList = line.split()

    # Line is a label
    # if lineList[0][-1] == ':':
    #     print lineList[0]

    while len(line) > 0:
        RemoveTabsandNewline(line)
        line = RemoveTabsandNewline(line)
        line = line.upper()
        lineList = line.split()

        # Takes care of blank lines
        if len(lineList) < 1:
            line = infile.readline()
            continue

        # Takes care of start. Only handles HEX for now.
        if lineList[0] == 'START':
            num = lineList[-1]
            num = '0x' + num
            if len(num) > 7:
                print "Start address bigger than 20 bits (5 digits)!"
                exit(1)
            # print num
            LocCtr = int(num, 0)
            # if (lineList[-1]).isdigit():
            #     LocCtr = int(lineList[-1])

        # Comment lines are skipped
        if lineList[0][0] == ".":
            line = infile.readline()
            continue

        # print lineList

        # Line is a label. Label inseted in SymTab, and label popped from
        # lineList
        if lineList[0][-1] == ':':
            if lineList[0][0:-1] in SymTab:
                print "Symbol repeated in table"
                exit(1)
            H_locCtr = HexLocCounter()
            SymTab[lineList[0][0:-1]] = H_locCtr
            lineList.pop(0)

            # should not work. Check why it does because you add : to keys
        elif ':' in lineList[0]:
            if lineList[0] in SymTab:
                print "Symbol repeated in table"
                exit(1)
            new = lineList[0].split(':')
            lineList.pop(0)
            elem1 = new[0]
            lineList.insert(0, new[1])
            H_locCtr = HexLocCounter()
            SymTab[elem1] = H_locCtr

        if len(lineList) > 1 and lineList[1][0] == "#" and ',' in lineList[1]:
            print("Extraneous characters at the end of line!")
            exit(1)

        # print lineList

        if len(lineList) > 0:

            if lineList[0][0] == "+":
                LocCtr += 4

            elif lineList[0] in OpTab:
                LocCtr += OpTab[lineList[0]][0]

            elif lineList[0] == "WORD":
                LocCtr += 3

                # TAKE CARE OF THIS SOME OTHER WAY PROBABLY
            elif lineList[0] == "BASE" or lineList[0] == "NOBASE":
                line = infile.readline()
                continue

            elif lineList[0] == "RESW":
                LocCtr += 3 * int(lineList[1])

            elif lineList[0] == "RESB":
                LocCtr += int(lineList[1])

            elif lineList[0] == "BYTE":
                if lineList[1][0] == 'C':
                    if lineList[-1][-1] != "'":
                        print "Instruction runs past the 40 line"
                        exit(1)
                    i = list(line).index("'")
                    LocCtr += len(line[i + 1:-1])
                elif lineList[1][0] == 'X':
                    i = list(line).index("'")
                    if lineList[1][-1] != "'":
                        print(lineList[-1][-1])
                        print "Instruction runs past the 40 line"
                        exit(1)
                    LocCtr += int(math.ceil((len(line[i:-1]) - 1) / 2.0))
                else:
                    LocCtr += 1

            elif lineList[0] == "END":
                size_end = LocCtr
                OutputSymTab()

        # match = re.match(r'^\s*(?P<label>[A-Za-z][A-Za-z0-9]*)', line)

        # if match:
        #     print match.group("label")
        #     print ("amin")

        line = infile.readline()

# -------------------------PASS 2------------------------------------------

    LocCtr = 0
    SIZE_T = 0

    infile = open(filename, "r")
    line = infile.readline()
    while len(line) > 0:
        RemoveTabsandNewline(line)
        line = RemoveTabsandNewline(line)
        line = line.upper()
        lineList = line.split()

        # Removes lines starting with comments
        if lineList[0][0] == ".":
            line = infile.readline()
            continue

        # If label found in the list, its popped
        if lineList[0][-1] == ':':
            lineList.pop(0)

        # if the line only contains a label, it will take care of it
        if len(lineList) == 0:
            line = infile.readline()
            continue



# _____________________________________________ SIC HANDLING___________________
        OpCode = "0"
        address = "0"
        operand1 = ""
        NFaddress = "0"
        # FIX THIS THING!!!!!
        if lineList[0] == "START":
            nostart = 1
            addressList.append("H")
            addressList.append("      ")
            startaddress = lineList[-1]
            LocCtr = int(("0x" + lineList[-1]), 0)
            while len(startaddress) != 6:
                startaddress = "0" + startaddress
            addressList.append(startaddress)
            size = size_end - int(("0x" + startaddress), 0)
            size = hex(size)[2:]
            while len(size) != 6:
                size = "0" + size
            addressList.append(size)
            addressList.append("T")
            line = infile.readline()
            continue

        # if there is no start
        if nostart == None:
            addressList.append("H")
            addressList.append("      ")
            startaddress = "0"
            LocCtr = 0
            while len(startaddress) != 6:
                startaddress = "0" + startaddress
            addressList.append(startaddress)
            size = size_end - int(("0x" + startaddress), 0)
            size = hex(size)[2:]
            while len(size) != 6:
                size = "0" + size
            addressList.append(size)
            addressList.append("T")
            nostart = 1

        # print line
        if lineList[0] == "BYTE":

            # calculates the the entry point for end
            if not END:
                tempLocCtr = hex(LocCtr)[2:]
                while len(tempLocCtr) != 6:
                    tempLocCtr = "0" + tempLocCtr
                END = tempLocCtr

            # If the last letter is T in the list, it appends the location address
            if addressList[-1] == "T":
                tempLocCtr = hex(LocCtr)[2:]
                while len(tempLocCtr) != 6:
                    tempLocCtr = "0" + tempLocCtr
                addressList.append(tempLocCtr)
                addressList.append("SIZE_T")

            num = lineList[-1]

            if lineList[1][0] == 'X':
                addressList.append((lineList[1][2:-1]).lower())
            elif lineList[1][0] == 'C':
                string = lineList[1][2:-1]
                hexvalstring = ""
                for i in string:
                    hexval = ord(i)
                    hexvalstring += hex(hexval)[2:]
                addressList.append(hexvalstring)
                # print addressList

            else:
                NFaddress = hex(int(num))[2:].upper()
                if len(NFaddress) != 2:
                    address = "0" + NFaddress
                    addressList.append(address)

            # FOR LENGTH HANDLING OF LocCtr
            if lineList[1][0] == 'C':
                i = list(line).index("'")
                LocCtr += len(line[i + 1:-1])
                SIZE_T += len(line[i + 1:-1])

            elif lineList[1][0] == 'X':
                i = list(line).index("'")
                if lineList[1][-1] != "'":
                    print(lineList[-1][-1])
                    print "Instruction runs past the 40 line"
                    exit(1)
                LocCtr += int(math.ceil((len(line[i:-1]) - 1) / 2.0))
                SIZE_T += int(math.ceil((len(line[i:-1]) - 1) / 2.0))

            else:
                NFaddress = hex(int(lineList[-1]))[2:]
                if len(NFaddress) != 2:
                    NFaddress = "0" + NFaddress
                addressList.append(NFaddress)
                LocCtr += 1
                SIZE_T += 1

        elif lineList[0] == "BASE":
            if (lineList[-1]).isdigit():
                base = hex(int(lineList[-1]))[2:]
            else:
                base = SymTab[lineList[-1]]


        elif lineList[0] == "NOBASE":
            base = None

        elif lineList[0] == "WORD":
            if addressList[-1] == "T":
                tempLocCtr = hex(LocCtr)[2:]
                while len(tempLocCtr) != 6:
                    tempLocCtr = "0" + tempLocCtr
                addressList.append(tempLocCtr)
                addressList.append("SIZE_T")


            # calculates the the entry point for end
            if not END:
                tempLocCtr = hex(LocCtr)[2:]
                while len(tempLocCtr) != 6:
                    tempLocCtr = "0" + tempLocCtr
                END = tempLocCtr

            #  for negative value of word
            if lineList[-1][0] == "-":
                print "aaa"
                binval = int(lineList[-1])
                binval = list(bin(binval))[3:]
                binval = ["0" if x == "1" else "1" for x in binval]

                binval = "".join(binval)
                binval = int(("0b" + binval), 0)
                binval += 1
                binval = str(binval)
                while len(binval) != 6:
                    binval = "f" + binval
                print "aa"
                addressList.append(binval)
                LocCtr += 3
                SIZE_T += 3
                line = infile.readline()
                continue



            num = lineList[-1]
            NFaddress = hex(int(num))[2:].upper()
            while len(NFaddress) != 6:
                NFaddress = "0" + NFaddress
            address = NFaddress
            addressList.append(address)
            LocCtr += 3
            SIZE_T += 3
            line = infile.readline()
            continue

        elif lineList[0] == "RESB":
            LocCtr += int(lineList[1])

            # Adds the size of t after the address and resets SIZE_T
            temp = hex(SIZE_T)[2:]
            if len(temp) != 2:
                temp = "0" + temp
            addressList = [temp if x == "SIZE_T" else x for x in addressList]
            SIZE_T = 0

            if addressList[-1] != "T":
                addressList.append("T")
            line = infile.readline()
            continue

        elif lineList[0] == "RESW":
            LocCtr += 3 * int(lineList[1])

            # Adds the size of t after the address and resets SIZE_T
            temp = hex(SIZE_T)[2:]
            if len(temp) != 2:
                temp = "0" + temp
            addressList = [temp if x == "SIZE_T" else x for x in addressList]
            SIZE_T = 0

            if addressList[-1] != "T":
                addressList.append("T")
            line = infile.readline()
            continue

        elif lineList[0] == "END":
            if addressList[-1] == "T":
                addressList.pop()
            # Adds the size of t after the address and resets SIZE_T
            temp = hex(SIZE_T)[2:]
            if len(temp) != 2:
                temp = "0" + temp
            addressList = [temp if x == "SIZE_T" else x for x in addressList]
            SIZE_T = 0

            addressList.append("E")
            addressList.append(END)
            OutputPass2(addressList, outfile)
            break
        else:
            # calculates the the entry point for end
            if not END:
                tempLocCtr = hex(LocCtr)[2:]
                while len(tempLocCtr) != 6:
                    tempLocCtr = "0" + tempLocCtr
                END = tempLocCtr

            # appends items necessary after T
            if addressList[-1] == "T":
                tempLocCtr = hex(LocCtr)[2:]
                while len(tempLocCtr) != 6:
                    tempLocCtr = "0" + tempLocCtr
                addressList.append(tempLocCtr)
                addressList.append("SIZE_T")

            if lineList[0][0] == "+":
                LocCtr += 4
                SIZE_T += 4
            elif lineList[0] in OpTab:
                #Handles extra input operands
                if len(OpTab[lineList[0]]) == 3:
                    if OpTab[lineList[0]][2] == 0:
                        if len(lineList) > 1:
                            print "Extra characters!"
                            exit(1)


                LocCtr += OpTab[lineList[0]][0]
                SIZE_T += OpTab[lineList[0]][0]

            format1 = None
            format2 = None
            format3 = None
            format4 = None

            n_bit = None
            i_bit = None
            x_bit = None
            b_bit = None
            p_bit = None
            e_bit = None

            if lineList[0][0] == "+":
                print "Welcome to format 4"
                format4 = 1
            elif OpTab[lineList[0]][0] == 1:
                format1 = 1
            elif OpTab[lineList[0]][0] == 2:
                format2 = 1
            elif OpTab[lineList[0]][0] == 3:
                format3 = 1


            # FORMAT 1 IS HANDLED HERE_________________________________________
            if format1 == 1:
                address = OpTab[lineList[0]][1]
                addressList.append(address)
                line = infile.readline()
                continue

            #  FORMAT 2 IS HANDLED HERE _______________________________________
            elif format2 == 1:
                instruction = 0
                if lineList[0] in OpTab.keys():
                    OpCode = OpTab[lineList[0]][1]
                    instruction = lineList[0]
                    lineList.pop(0)



                op1 = "0"
                op2 = "0"

                templine = "".join(lineList)
                templine = ["" if x == " " else x for x in templine]
                templine = "".join(templine)

                if "," in templine:
                    templine = templine.split(",")

                    if (OpTab[instruction][-1] == 1):
                        print "Illegal number of instructions!"
                        exit(1)
                    elif OpCode == "B0":
                            print "Wrong format!"
                            exit(1)

                    op1 = str(OpTab[templine[0]][0])
                    if (templine[1]).isdigit():
                        op2 = hex(int(templine[1]) - 1)[2:]
                    else:
                        op2 = str(OpTab[templine[1]][0])

                elif "," not in templine:
                    # print line

                    if (lineList[0]).isdigit():
                        op1 = lineList[0]
                    else:
                        # print "Wrong format!"
                        # exit(1)
                        # print "mara"
                        if OpCode == "B0":
                            print "Wrong format!"
                            exit(1)
                        op1 = str(OpTab[lineList[0]][0])
                else:
                    "print case not handled format2"

                if len(OpCode) < 2:
                    OpCode = "0" + OpCode

                NFaddress = OpCode + op1 + op2
                address = NFaddress
                addressList.append(address)

                line = infile.readline()
                continue

            # ________________________________________________________________________

            # FORMAT 4 IS HANDLED HERE_________________________________________

            #  , x not handles
            #  only handles one operand that has to be in SymTab
            elif format4 == 1:

                x_bit = 0
                searchx = re.search(r',[ ]*[X]$', line)
                if searchx:
                    x_bit = 1


                #  Assigns opcode the proper value and shifts left by 21
                if lineList[0][1:] in OpTab.keys():
                    OpCode = OpTab[lineList[0][1:]][1]
                    OpCode = "0x" + OpCode

                    OpCodeShifted = int(OpCode, 0) << 24

                    lineList.pop(0)

                my_e_bit = 1 << 20
                my_i_bit = 1 << 24
                my_n_bit = 1 << 25
                my_x_bit = 0

                operand1 = 0
                operand2 = 0

                if x_bit == 1:
                    if "," in line:
                        line1 = " ".join(lineList)
                        line1 = ["" if x == " " else x for x in line1]
                        line1 = " ".join(lineList)
                        line1list = line1.split(",")
                        operand1 = line1list[0]
                        operand2 = line1list[-1]
                        my_x_bit = 1 << 23



                if lineList[0][0] == "#":
                    my_n_bit = 0
                    NFaddress = SymTab[lineList[0][1:]]
                elif lineList[0][0] == "@":
                    my_i_bit = 0
                    NFaddress = SymTab[lineList[0][1:]]
                elif x_bit == 1:
                    NFaddress = SymTab[operand1]

                else:
                    NFaddress = SymTab[lineList[0]]

                NFaddress = int(("0x" + NFaddress), 0)


                address = hex(OpCodeShifted + NFaddress + my_e_bit + my_i_bit + my_n_bit + my_x_bit)[2:]
                while len(address) != 8:
                    address = "0" + address
                addressList.append(address)


                line = infile.readline()
                continue

                # __________________________________________________________________


            # FORMAT 3 IS HANDLED HERE _________________________________________________


            if "@" in line:
                n_bit = 1

            if "#" in line:
                i_bit = 1

            # sets the x bit if , x found in the line
            searchx = re.search(r',[ ]*[X]$', line)
            if searchx:
                x_bit = 1

            if "+" in line:
                e_bit = 1

            # gets the opcode for the instruction and pops the instruction
            if lineList[0] in OpTab.keys():
                OpCode = OpTab[lineList[0]][1]
                lineList.pop(0)

            # Finds operand 1 and 2 if more than 1 operands
            if "," in line:
                line1 = " ".join(lineList)
                line1 = ["" if x == " " else x for x in line1]
                line1 = " ".join(lineList)
                line1list = line1.split(",")
                operand1 = line1list[0]
                operand2 = line1list[-1]
                if operand2 != "X":
                    "You have not handled this case!  1"
            elif len(lineList) == 1:
                operand1 = lineList[0]

            if operand1 != "" and (operand1[0] == "#" or operand1[0] == "@"):
                operand1 = operand1[1:]

            if (operand1 in SymTab.keys()):
                NFaddress = SymTab[operand1]
            elif operand1 != "":
                print "Operand not found in Symtab!"
                exit(1)

            # BASE IS HANDLED HERE_______________________________________

            baseaddress = int(("0x" + NFaddress), 0)
            if baseaddress >= (2 ** 12) and base:
                print base
                decbase = "0x" + base
                decbase = int(decbase, 0)
                if (baseaddress - int(base)) > 0:
                    address = baseaddress - decbase

                    OpCode = "0x" + OpCode
                    OpCodeShifted = int(OpCode, 0) << 16

                    bmy_n_bit = 1
                    bmy_i_bit = 1
                    bmy_b_bit = 1

                    bmy_n_bit = 1 << 17
                    bmy_i_bit = 1 << 16
                    bmy_b_bit = 1 << 14

                    if i_bit == 1 and n_bit is None:

                        NFaddress = int(("0x" + NFaddress), 0)

                        mynum = OpCodeShifted + address + bmy_i_bit + bmy_b_bit
                        address = hex(mynum)[2:]

                        while len(address) <= 5:
                            address = "0" + address
                        addressList.append(address)

                        line = infile.readline()
                        continue

                    if n_bit == 1 and i_bit is None:
                        NFaddress = int(("0x" + NFaddress), 0)

                        mynum = OpCodeShifted + address + bmy_n_bit + bmy_b_bit
                        address = hex(mynum)[2:]

                        while len(address) <= 5:
                            address = "0" + address
                        addressList.append(address)

                        line = infile.readline()
                        continue

                    bmy_x_bit = 0
                    if x_bit == 1:
                        print "aaaa"
                        bmy_x_bit = 1

                    bmy_n_bit = 1
                    bmy_i_bit = 1
                    bmy_b_bit = 1

                    bmy_n_bit = 1 << 17
                    bmy_i_bit = 1 << 16
                    bmy_b_bit = 1 << 14
                    bmy_x_bit = bmy_x_bit << 15

                    NFaddress = int(("0x" + NFaddress), 0)

                    mynum = OpCodeShifted + address + bmy_n_bit + bmy_i_bit + bmy_b_bit + bmy_x_bit
                    address = hex(mynum)[2:]

                    while len(address) <= 5:
                        address = "0" + address
                    addressList.append(address)

                    line = infile.readline()
                    continue

    # # PC RELATIVE is handled here____________________________________________

    # baseaddress = int(("0x" + NFaddress), 0)

            elif baseaddress >= (2 ** 12):
                print baseaddress

                OpCode = "0x" + OpCode
                OpCodeShifted = int(OpCode, 0) << 16

                pc_start_address = LocCtr
                pc_address_diff = 0

                print "base"
                print hex(baseaddress)

                pc_address_diff = baseaddress - pc_start_address

                if pc_address_diff >= 2 ** 12:
                    print line
                    print LocCtr
                    print "Extended bit not set"
                    exit(1)
                # pc_address_diff = (pc_address_diff)

                pmy_n_bit = 1
                pmy_i_bit = 1
                pmy_p_bit = 1

                pmy_n_bit = 1 << 17
                pmy_i_bit = 1 << 16
                pmy_p_bit = 1 << 13
                pmy_x_bit = 0

                if lineList[0][0] == "#":
                    pmy_n_bit = 0

                if lineList[0][0] == "@":
                    pmy_i_bit = 0

                if x_bit == 1:
                    pmy_x_bit = 1 << 15


                mynum = OpCodeShifted + pc_address_diff + pmy_n_bit + pmy_i_bit + pmy_p_bit + pmy_x_bit
                address = hex(mynum)[2:]

                while len(address) <= 5:
                    address = "0" + address
                addressList.append(address)

                print hex(LocCtr)



                line = infile.readline()
                continue

    # ______________________________________________________________________________

        #  SIMPLE SIC/XE INSTRUCTIONS

            #  If n_bit is set
            elif n_bit == 1:
                OpCode = "0x" + OpCode
                OpCodeShifted = int(OpCode, 0) << 16

                smy_n_bit = 1
                smy_n_bit = 1 << 17

                NFaddress = int(NFaddress, 0)

                mynum = OpCodeShifted + NFaddress + smy_n_bit
                address = hex(mynum)[2:]

                while len(address) <= 5:
                    address = "0" + address
                addressList.append(address)

                line = infile.readline()
                continue

            elif i_bit == 1:
                OpCode = "0x" + OpCode
                OpCodeShifted = int(OpCode, 0) << 16

                smy_n_bit = 1
                smy_i_bit = 1 << 16

                NFaddress = int(NFaddress, 0)

                mynum = OpCodeShifted + NFaddress + smy_i_bit
                address = hex(mynum)[2:]

                while len(address) <= 5:
                    address = "0" + address
                addressList.append(address)

                line = infile.readline()
                continue




            if x_bit:
                # print "a"
                OpCode = "0x" + OpCode
                OpCodeShifted = int(OpCode, 0) << 16
                NFaddress = int(("0x" + NFaddress), 0)
                x_bit_value = 32768
                address = hex(OpCodeShifted + NFaddress + x_bit_value)[2:]
                while len(address) != 6:
                    address = "0" + address
                addressList.append(address)
                # print address
            else:
                OpCode = "0x" + OpCode
                OpCodeShifted = int(OpCode, 0) << 16
                NFaddress = int(("0x" + NFaddress), 0)
                address = hex(OpCodeShifted + NFaddress)[2:]
                while len(address) != 6:
                    address = "0" + address
                addressList.append(address)

        # print line
        # print(address)

# ___________________________________________________________________________________________25/44 64%



        line = infile.readline()


if __name__ == "__main__":
    main()
