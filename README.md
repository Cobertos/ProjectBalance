# Projected Balance Calculator

Creates a plot of the projected balances of an account based on one-time and recurring transactions.
To configure, go into the code and define your transactions in the main function (should be easy
to figure out what needs to be done). Transaction objects can take either a [dateutil.rrule](https://dateutil.readthedocs.io/en/stable/rrule.html) or a
plain datetime.

## Dependencies
* [python-dateutil](https://pypi.python.org/pypi/python-dateutil)
* [plotly](https://pypi.python.org/pypi/plotly)