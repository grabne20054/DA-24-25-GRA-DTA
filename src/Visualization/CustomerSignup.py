import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import matplotlib.pyplot as plt
from DataAnalysis.descriptive.CustomerSignup import CustomerSignup

if __name__ == "__main__":
    customer_signup = CustomerSignup()
    data = customer_signup.perform()

    yearly_growth = data["growth"]
    cumulative_growth = data["cumulative_growth"]

    years = list(yearly_growth.keys())
    customers_per_year = list(yearly_growth.values())
    cumulative_customers = list(cumulative_growth.values())


    plt.figure(figsize=(10, 6))

    plt.fill_between(years, customers_per_year, color="skyblue", alpha=0.4)
    plt.plot(years, cumulative_customers, color="Slateblue", alpha=0.6, label="Cumulative Growth")

    plt.xlabel("Year")
    plt.ylabel("Customers")
    plt.title("Yearly and Cumulative Growth of Customers")
    plt.legend()
    plt.grid()
    plt.show()