from decimal import *
import hashlib
import datetime
import csv
import pdfkit

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



class Account:
    def __init__(self, accountID, accountName, openingBalance, openingDR, dateRange):
        self.accountID = accountID
        self.dateRange = dateRange
        if openingBalance == "-":
            self.initialBalance = self.formatNumber(0)
        else:
            self.initialBalance = self.formatNumber(openingBalance)
        self.accountName = accountName
        self.openingDR = openingDR
        self.deposits = self.formatNumber(0)
        self.lease = self.formatNumber(0)
        self.envelope = self.formatNumber(0)
        self.expense = self.formatNumber(0)
        self.income = self.formatNumber(0)
        self.balanceForward = self.formatNumber(0)
        self.events = []
        self.service = self.formatNumber(0)
        self.insurance = self.formatNumber(0)
        self.wifi = self.formatNumber(0)
        self.transferin = self.formatNumber(0)
        self.transferout = self.formatNumber(0)

    def resetAccount(self):
        self.lease = self.formatNumber(0)
        self.envelope = self.formatNumber(0)
        self.expense = self.formatNumber(0)
        self.income = self.formatNumber(0)
        self.balanceForward = self.formatNumber(0)
        self.deposits = self.formatNumber(0)
        self.service = self.formatNumber(0)
        self.insurance = self.formatNumber(0)
        self.wifi = self.formatNumber(0)
        self.transferin = self.formatNumber(0)
        self.transferout = self.formatNumber(0)

    def getAccountID(self):
        return self.accountID
    def formatNumber(self, inp): #formats to 2 places
        return Decimal(inp).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

    def invertFormatNumber(self, inp):
        inp = Decimal(inp)
        return Decimal(Decimal(inp * -1).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))

    def getCost(self, lineval):
        if lineval[6] == "-":
            return self.formatNumber(lineval[7])#credits
        elif lineval[7] == "-":
            return self.invertFormatNumber(lineval[6])#Debits
        else:
            return 0

    def parseLine(self, lineval):
        if len(lineval) > 3 and lineval[2] != "": #account item
            linePrice = self.getCost(lineval)
            if lineval[4] == "lease":
                self.events.append({"name":lineval[3],"price":linePrice,"date":lineval[2], "type": "lease"})
            elif lineval[4] == "deposit":
                self.events.append({"name":lineval[3],"price":linePrice,"date":lineval[2], "type": "deposit"})
            elif linePrice > 0 and lineval[3] == "" and lineval[4] != "transfer" and lineval[4] != "TRANSFER": #envelope
                self.events.append({"name":lineval[4],"price":linePrice,"date":lineval[2], "type": "envelope"})
            elif linePrice > 0 and lineval[4] == "transfer": #transfer in
                self.events.append({"name":lineval[4],"price":linePrice,"date":lineval[2], "type": "transfer_in"})

            elif linePrice < 0 and lineval[4] == "Insurance": #insurance
                self.events.append({"name":lineval[4],"price":linePrice,"date":lineval[2], "type": "insurance"})
            elif linePrice < 0 and lineval[4] == "Service Fee": #service fee
                self.events.append({"name":lineval[4],"price":linePrice,"date":lineval[2], "type": "service"})
            elif linePrice < 0 and lineval[4] == "wifi": #wifi
                self.events.append({"name":lineval[4],"price":linePrice,"date":lineval[2], "type": "wifi"})
            elif linePrice < 0 and lineval[4] == "transfer": #transfer out
                self.events.append({"name":lineval[4],"price":linePrice,"date":lineval[2], "type": "transfer_out"})

            elif linePrice < 0 and lineval[3] == "": #mystery
                self.events.append({"name":lineval[4],"price":linePrice,"date":lineval[2], "type": "expense"})
            elif linePrice > 0 and lineval[3] == "": #positive mystery
                self.events.append({"name":lineval[4],"price":linePrice,"date":lineval[2], "type": "income"})
            elif linePrice < 0: #expense
                self.events.append({"name":lineval[3],"price":linePrice,"date":lineval[2], "type": "expense"})
            elif linePrice > 0: #income
                self.events.append({"name":lineval[3],"price":linePrice,"date":lineval[2], "type": "income"})
            else:
                print("skiped line")
    def formatCost(self, cost):
        if cost > 0:
            return str("$" + str(cost).rjust(10) + " ").replace(" ", "&nbsp;")
        elif cost < 0:
            return "$" + str("(" + str(cost*-1) + ")").rjust(11).replace(" ", "&nbsp;")
        else:
            return str("$" + str(cost).rjust(10) + " ").replace(" ", "&nbsp;")

    def calculateExpenses(self):
        self.resetAccount()
        for event in self.events:
            if event["type"] == "lease":
                self.lease += event["price"]
            elif event["type"] == "envelope":
                self.envelope += event["price"]
            elif event["type"] == "expense":
                self.expense += event["price"]
            elif event["type"] == "income":
                self.income += event["price"]
            elif event["type"] == "deposit":
                self.deposits +=  event["price"]
            elif event["type"] == "insurance":
                self.insurance += event["price"]
            elif event["type"] == "service":
                self.service += event["price"]
            elif event["type"] == "wifi":
                self.wifi += event["price"]
            elif event["type"] == "transfer_in":
                self.transferin += event["price"]
            elif event["type"] == "transfer_out":
                self.transferout += event["price"]
        if self.openingDR == "Dr":
            thisInitialBalance = self.initialBalance * -1
        else:
            thisInitialBalance = self.initialBalance
        self.balanceForward = thisInitialBalance + self.deposits

    def generate(self, carTemplatePath):

        cartemplatefile = open(carTemplatePath, 'r')
        cartemplatestring = cartemplatefile.read()



        self.calculateExpenses()
        totalIncome = self.income + self.lease + self.envelope + self.transferin
        totalExpense = self.expense + self.insurance + self.service + self.wifi
        transactionSection = ""
        transactionExpense = ""
        for event in self.events:
            if event["price"] < 0 and event["type"] != "deposit":
                transactionExpense += "<tr><td>" + str(event["name"][:50].ljust(50).replace(" ", "&nbsp;")  + " " + str(event["date"]).rjust(9).replace(" ", "&nbsp;")).replace(" ", "&nbsp;") + "</td><td><p class=\"table-data\">" + self.formatCost(event["price"]) + "</p></td></tr>"
            else:
                transactionSection += "<tr><td>" + str(event["name"][:50].ljust(50).replace(" ", "&nbsp;")  + " " + str(event["date"]).rjust(9).replace(" ", "&nbsp;")).replace(" ", "&nbsp;") + "</td><td><p class=\"table-data\">" + self.formatCost(event["price"]) + "</p></td></tr>"
        
        notesSection = "Generated on " + str(datetime.datetime.now()) + "<br/>"
        notesSection += "Vancouver Taxi Ltd.<br/>"
        notesSection += "790 Clark Drive Vancouver BC<br/>"

        cartemplatestring = cartemplatestring.replace('$OPENING_BALANCE', str(self.formatCost(self.balanceForward)))
        cartemplatestring = cartemplatestring.replace('$LEASE', str(self.formatCost(self.lease)))
        cartemplatestring = cartemplatestring.replace('$ENVELOPES', str(self.formatCost(self.envelope)))
        cartemplatestring = cartemplatestring.replace('$OTHER_CREDIT', str(self.formatCost(self.income)))
        cartemplatestring = cartemplatestring.replace('$TRANSFER_IN', str(self.formatCost(self.transferin)))
        cartemplatestring = cartemplatestring.replace('$TOTAL_INCOME', str(self.formatCost(totalIncome) ))
        cartemplatestring = cartemplatestring.replace('$SERVICE', str(self.formatCost(self.service)))
        cartemplatestring = cartemplatestring.replace('$INSURANCE', str(self.formatCost(self.insurance)))
        cartemplatestring = cartemplatestring.replace('$WIFI', str(self.formatCost(self.wifi)))
        cartemplatestring = cartemplatestring.replace('$TRANSFER_OUT', str(self.formatCost(self.transferout)))
        cartemplatestring = cartemplatestring.replace('$OTHER_EXPENSE', str(self.formatCost(self.expense)))
        cartemplatestring = cartemplatestring.replace('$TOTAL_EXPENSE', str(self.formatCost(totalExpense)))
        cartemplatestring = cartemplatestring.replace('$FINAL_BALANCE', str(self.formatCost(totalIncome + totalExpense + self.balanceForward + self.transferout)))

        cartemplatestring = cartemplatestring.replace('$CAR_NAME', str(self.accountName))
        cartemplatestring = cartemplatestring.replace('$DATERANGE', str(self.dateRange))
        cartemplatestring = cartemplatestring.replace('$TRANSACTION_DATA', transactionSection)
        cartemplatestring = cartemplatestring.replace('$TRANSACTION_EXPENSE_DATA', transactionExpense)
        cartemplatestring = cartemplatestring.replace('$NOTES', notesSection)
        return cartemplatestring

#PDFkit global Constants
path_wkthmltopdf = r'wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
options = {
    'quiet': ''
    }
print("enter the file")
thisfile = input()
print("enter the date range")
dateRange = input()
output = ""
with open(thisfile) as ownerids:
    #read line by line
    accounts = []
    reader = csv.reader(ownerids)
    for lineval in reader:
        firstcol = lineval[0]
        for cnt, col in enumerate(lineval):
            lineval[cnt] = col.replace(",", "")
        if len(firstcol) > 1 and firstcol[1] == "2": #start of an account
            accounts.append(Account(lineval[0],lineval[1], lineval[8], lineval[9], dateRange))#create new account
            print("account")
        elif len(accounts) > 0: 
            accounts[-1].parseLine(lineval)
        else:
            print("blank csv line")
accountcount = len(accounts)
accoundtex = 1
hashsalt = "+qh!T<t<R$~m9bF"
for thisAccount in accounts:
    output = thisAccount.generate("templates/car-template.html")
    filename = 'statements/car/' + str(hashlib.sha256(str(thisAccount.getAccountID() + hashsalt).encode('utf-8')).hexdigest())[:10] + ".pdf"
    filename2 = 'statements/car/' + str(thisAccount.getAccountID()) + ".pdf"
    carthistemplatefilename = 'statements/car/thiscar.html' #temporary html file for further processing into pdf
    carthistemplatefile = open(carthistemplatefilename, 'w')
    carthistemplatefile.write(output)
    carthistemplatefile.close()
    pdfkit.from_file(carthistemplatefilename, filename,options = options, configuration = config) #save temp HTML file as properly named PDF
    pdfkit.from_file(carthistemplatefilename, filename2,options = options, configuration = config) #save temp HTML file as properly named PDF
    print("Saving file " + str(accoundtex) + " of " + str(accountcount))
    accoundtex += 1