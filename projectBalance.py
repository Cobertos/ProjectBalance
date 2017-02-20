from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY
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
        return isinstance(self.when, datetime) and self.when.date() == dayTime.date() \
            or isinstance(self.when, rrule) and dayTime in self.when

def projectBalances(transactions, startAmount, fromDate, toDate):
    balances = []
    for day in rrule(DAILY, dtstart=fromDate, until=toDate):
        #Calculate the sum of all charges for given day
        ts = transactions[:]
        amnts = map((lambda t: t.getAmountForDay(day)), ts)
        tSum = balances[-1] if balances else startAmount
        for amnt in amnts:
            tSum += amnt
        #Append to balances
        balances.append(tSum)

    return balances

#def getTransactionsFromFile(filePath):

def createBalanceGraph(balances, fromDate, toDate):
    dayLabels = rrule(DAILY, dtstart=fromDate, until=toDate)
    dayLabels = map((lambda dt: dt.strftime("%a, %b %d")), dayLabels)
    dayLabels = list(dayLabels)
    trace = go.Scatter(x=dayLabels, y=balances)

    offline.plot( [trace], filename="projectedBalanceGraph")

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

    #Project Balances
    ts = [
        t,
        t2,
    ]
    bs = projectBalances(ts, 10, ds[0], ds[4])
    assert(tuple(bs) == (30, 50, 70, 70, 70))

    #Create Balance Graph
    #createBalanceGraph(bs, ds[0], ds[4]) #WORKS

def main():
    #DEFINE ALL BUDGETARY CONSTRAINTS
    transactions = []

    #END DEFINE
    #Do the actual work
    fromDate = datetime.today()
    toDate = datetime.today() + timedelta(days=100)
    balances = projectBalances(1800, fromDate, toDate, transactions)
    createBalanceGraph(balances, fromDate, toDate)

if __name__ == "__main__":
    test()
    main()