from decimal import *
import datetime
import csv
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

    def resetAccount(self):
        self.lease = self.formatNumber(0)
        self.envelope = self.formatNumber(0)
        self.expense = self.formatNumber(0)
        self.income = self.formatNumber(0)
        self.balanceForward = self.formatNumber(0)
        self.deposits = self.formatNumber(0)
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
            elif linePrice < 0 and lineval[3] == "": #mystery
                self.events.append({"name":lineval[4],"price":linePrice,"date":lineval[2], "type": "income"})
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
            return "$" + str(cost).rjust(10)
        elif cost < 0:
            return "$" + str("(" + str(cost*-1) + ")").rjust(11)
        else:
            return "$" + str(cost).rjust(10)

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
        if self.openingDR == "Dr":
            thisInitialBalance = self.initialBalance * -1
        else:
            thisInitialBalance = self.initialBalance
        self.balanceForward = thisInitialBalance - self.deposits

    def generate(self):
        statement = "Account Summary For " + str(self.accountName) + "\n"
        statement += "Account Number: " + str(self.accountID) + "\n"
        statement += "Date:" + self.dateRange + "\n"
        statement += "\n"
        self.calculateExpenses()
        totalIncome = self.income + self.lease + self.envelope
        totalExpense = self.expense
        summarySection = ""
        statement += "MONTHLY SUMMARY\n"
        statement += "---------------------------------------------------------------\n"
        summarySection += "OPENING BALANCE:".ljust(51)+ self.formatCost(self.balanceForward) + "\n"
        summarySection += "INCOME\n"
        summarySection += "  Lease:".ljust(51) + self.formatCost(self.lease) + "\n"
        summarySection += "  Envelopes:".ljust(51) + self.formatCost(self.envelope) + "\n"
        summarySection += "  Other Credits:".ljust(51) + self.formatCost(self.income) + "\n"
        summarySection += "TOTAL INCOME:".ljust(51) +  self.formatCost(totalIncome) + "\n"
        summarySection += "TOTAL EXPENSE:".ljust(51) +  self.formatCost(totalExpense * -1) + "\n"
        summarySection += "BALANCE:".ljust(51) + self.formatCost(totalIncome + totalExpense + self.balanceForward) + "\n"
        statement += summarySection
        statement += "\n"
        statement += "TRANSACTIONS" + "\n"
        statement += "---------------------------------------------------------------\n"
        transactionSection = ""
        for event in self.events:
            transactionSection += event["name"][:40].ljust(40)  + " " + str(event["date"]).rjust(9) + " " + self.formatCost(event["price"]) + "\n"
        statement += transactionSection
        statement += "\n"
        statement += "---------------------------------------------------------------\n"
        statement += "Generated on " + str(datetime.datetime.now()) + "\n"
        statement += "Vancouver Taxi Ltd.\n"
        statement += "790 Clark Drive Vancouver BC\n"
        return statement
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
for thisAccount in accounts:
    output = thisAccount.generate()
    filename = str(thisAccount.getAccountID()) + ".txt"
    servicelog = open(filename, 'w')
    servicelog.write(output)
    servicelog.close()