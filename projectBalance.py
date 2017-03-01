import math
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY, YEARLY, MONTHLY, WEEKLY
import plotly.offline as offline
import plotly.graph_objs as go

class Transaction:
    """
    Represents an .amount that's charged every
    .when (a specific date or a reoccuring rule)
    """

    def __init__(self, when, amount):
        if(when == None or amount == None):
            raise ValueError("Transaction missing required constructor parameter...")
        if(not (isinstance(when, datetime) or isinstance(when, rrule))):
            raise ValueError("Transaction .when was not correct type")
        self.when = when #A datetime object, or rrule
        self.amount = amount #Number

    def getAmountForDay(self, dayTime):
        """
        Returns the amount that this transaction will cause for a given day
        """
        return self.amount if self.doesTransactForDay(dayTime) else 0

    def doesTransactForDay(self, dayTime):
        """
        Returns boolean if this transaction will cause a charge on the given day
        """
        #If datetime, just return if the dates are equal, if a rrule, map to date()s and check in list
        return isinstance(self.when, datetime) and self.when.date() == dayTime.date() \
            or isinstance(self.when, rrule) and dayTime.date() in map(lambda dt: dt.date(), self.when)

def projectDiffs(transactions, fromDate, toDate):
    """
    Projects the differences in balance from the previous day for all dats in
    fromDate to toDate using the transactions defined
    """
    diffs = []
    for day in rrule(DAILY, dtstart=fromDate, until=toDate):
        #Calculate the sum of all charges for given day
        ts = transactions[:]
        amnts = map((lambda t: t.getAmountForDay(day)), ts)
        tSum = sum(amnts)
        #Append to diffs
        diffs.append(tSum)

    return diffs

#def getTransactionsFromFile(filePath):

def createBalanceGraph(diffs, fromDate, toDate, startAmount, saveProportion, displayLowerLimit):
    dayLabels = rrule(DAILY, dtstart=fromDate, until=toDate)
    dayLabels = map((lambda dt: dt.strftime("%a, %b %d")), dayLabels)
    dayLabels = list(dayLabels)

    print(saveProportion)

    balances = []
    saveBalances = []
    currentBalance = currentSaveBalance = startAmount
    for diff in diffs:
        currentBalance += diff
        balances.append(currentBalance)

        currentSaveBalance += diff if diff < 0 else (diff * (1-saveProportion))
        saveBalances.append(currentSaveBalance)
        

    lowerLimitBalances = []
    currentLowerLimit = math.inf
    #Run through balances backward (because lower limit can only
    #be known from the future expenses) and prepend to get it
    #back into the same order
    for i, balance in reversed(list(enumerate(saveBalances))):
        currentLowerLimit = min(balance,currentLowerLimit)
        lowerLimitBalances.insert(0, currentLowerLimit)

    trace0 = go.Scatter(x=dayLabels, y=balances,
        fill="tonexty", mode="none", name="Balance", fillcolor="rgba(31, 119, 180, 0.5)")
    trace1 = go.Scatter(x=dayLabels, y=saveBalances,
        fill="tonexty", mode="none", name="Balance with %%%.2f savings" % ((saveProportion)*100), fillcolor="rgba(255, 127, 14, 0.5)")
    trace2 = go.Scatter(x=dayLabels, y=lowerLimitBalances,
        fill="tozeroy", mode="none", name="Maximum Unplanned Expenditures", fillcolor="rgba(44, 160, 44, 0.5)")

    data = [trace2, trace1, trace0]
    layout = go.Layout(showlegend=True,
    yaxis={
        "type":"linear",
        "tickprefix":"$"
    })

    fig = go.Figure(data=data, layout=layout)
    offline.plot(fig, filename="projectedBalanceGraph")

def test():
    ds = list(rrule(DAILY, dtstart=datetime(2012,12,20), until=datetime(2012,12,24))) #5 days, 20th-24th

    #Transaction - Simple datetime.datetime
    t = Transaction(ds[0], 20)
    assert(t.doesTransactForDay(ds[0]))
    assert(t.getAmountForDay(ds[0]) == 20)

    #Transaction - dateutil.rrule
    r = rrule(DAILY, dtstart=ds[1], until=ds[2])
    t2 = Transaction(r, 20)
    assert(not t2.doesTransactForDay(ds[0]))
    assert(t2.doesTransactForDay(ds[1]))
    assert(t2.doesTransactForDay(ds[2]))
    assert(not t2.doesTransactForDay(ds[3]))

    #Project Transactions
    ts = [
        t,
        t2,
    ]
    bs = projectDiffs(ts, ds[0], ds[4])
    assert(tuple(bs) == (20, 20, 20, 0, 0))

    #Create Balance Graph
    #createBalanceGraph(bs, ds[0], ds[4]) #WORKS

def main():

    startAmount = 1800
    fromDate = datetime.today()
    toDate = datetime.today() + timedelta(days=400)

    #DEFINE ALL BUDGETARY CONSTRAINTS - These are just examples
    savePercentage = 30
    transactions = [
        #INCOME
        Transaction(rrule(WEEKLY,  dtstart=datetime(2017,2,17), until=toDate, interval=2),              1500),   #+1500/biweekly from a specific Friday as the start (like a salary)

        #CHARGES
        Transaction(rrule(YEARLY,  dtstart=fromDate, until=toDate, bymonth=1, bymonthday=9),            -50),    #50/year charged on 1/9
        Transaction(rrule(MONTHLY, dtstart=fromDate, until=toDate, bymonth=[6,12], bymonthday=10),      -5000),  #5000/bi-yearly charged 6/10 and 12/10
        Transaction(rrule(MONTHLY, dtstart=fromDate, until=toDate, bymonthday=9),                       -100),   #100/month charged every 9th
        Transaction(rrule(MONTHLY, dtstart=fromDate, until=toDate, bymonthday=1),                       -40),    #40/month charged every 1st
        Transaction(rrule(MONTHLY, dtstart=fromDate, until=toDate, bymonthday=-1),                      -50),    #50/month charged on last day of month
        Transaction(rrule(MONTHLY, dtstart=fromDate, until=toDate, bymonthday=22),                      -228)    #250/monthly on the 22nd
    ]
    displayLowerLimit = True
    #END DEFINE

    saveProportion = min(savePercentage/100,1)

    #Do the actual work
    diffs = projectDiffs(transactions, fromDate, toDate)
    createBalanceGraph(diffs, fromDate, toDate, startAmount, saveProportion, displayLowerLimit)

if __name__ == "__main__":
    test()
    main()