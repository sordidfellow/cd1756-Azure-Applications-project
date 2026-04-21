import pyodbc

drivers = pyodbc.drivers()
for driver in drivers:
    print(driver)