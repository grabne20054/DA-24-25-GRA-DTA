import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from DataAnalysis.descriptive.EmployeeAmount import EmployeeAmount
from matplotlib import pyplot as plt

if __name__ == "__main__":
    employee_amount = EmployeeAmount()
    data = employee_amount.perform()

    plt.bar(data.keys(), data.values())
    plt.show()
    