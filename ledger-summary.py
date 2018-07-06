from decimal import *
def formatDriverAccount(driverId):
    idString = str(driverId)
    if len(idString) > 6:
        idString = "23" + idString[-6:]
    else:
        idString = "23" + idString.ljust(6,"0")
    return idString
def formatCarAccount(car, shift):
    shiftString = str(int(shift + 1)) #shift up shift type by 1
    carString = str(car)
    if carString[0] == "7" and len(carString) > 2:
        shiftString = "3"
    carString = carString.rjust(3,"0") #pad car number with 0s to the right
    carString = "22" + carString.ljust(5,"0") + shiftString
    return carString
def invertFormatNumber(inp):
    inp = Decimal(inp)
    return Decimal(Decimal(inp * -1).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
def formatNumber(inp):
    return Decimal(inp).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

print("enter the file")
thisfile = input()
print("enter the date mm-dd-yy")
date = input()
print("enter the source")
source = input()
output = ""
output += date + "," + source + "," + "deposit from april statement\n"
with open(thisfile) as ownerids:
    #read line by line
    for cnt, line in enumerate(ownerids):
        lineval = line.replace('\n', "").split(",")
        if cnt == 0:
            print("skip")
            accounts = line.replace('\n', "").split(",") #get accounts from top row
        else:
            driverid = formatDriverAccount(lineval[0])
            for cntcol, linecol in enumerate(lineval):
                print(linecol)
                if cntcol > 0 and linecol != "" and linecol != "0" and Decimal(linecol) > 0:
                    output += str(driverid) + "," + str(formatNumber(linecol)) + "\n"
                    output += str(accounts[cntcol]) + "," + str(invertFormatNumber(linecol)) + "\n"
                else:
                    print("skip blank")

filename = source + ".csv"
servicelog = open(filename, 'w')
servicelog.write(output)
servicelog.close()