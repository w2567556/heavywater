import unittest
import numpy as np

def calculate_future_value(p, n, r, y, d):
    """
    p = initial value = 2500
    n = compounding periods per year = 12
    r = nominal interest rate, compounded n times per year = 4% annual interest rate = 0.04 
    i = periodic interest rate = r/n = 0.04/12 = 0.00333333
    y = number of years = 5
    t = number of compounding periods = n*y = 12*5 = 60
    d = periodic deposit = 100
    The formula for the future value of an annuity due is d*(((1 + i)^t - 1)/i)*(1 + i)
    https://money.stackexchange.com/questions/16507/calculate-future-value-with-recurring-deposits
    """
    i = float(r)/n
    t = n*y
    # future value of an annuity due
    # this is how much the fixed deposits are going to be worth at the end time period
    fv = d*(((1 + i)**t - 1)/i)*(1 + i)
    # present future value
    # this is how much the initial deposit is going to be worth at the end of the time period
    pfv =  p*((1 + i)**t)
    total = pfv + fv
    return total

def example_monthly_snp_future_value(principal,years):
    """
    https://en.wikipedia.org/wiki/S%26P_500_Index shows 5 year return of 15.79% for 2017
    principal and deposit amounts are the same
    """
    return calculate_future_value(principal, 12, 0.1579, years, principal)

def example_monthly_savings_future_value(principal,years):
    """
    No interest add
    """
    return principal*12*years





class TestMaths(unittest.TestCase):
    def setUp(self):
        pass

    def test_future_value(self):
        np.testing.assert_almost_equal(
            calculate_future_value(
                2500,
                12,
                0.04,
                5,
                100
            ), 9704.49, decimal=2, verbose=True)


if __name__ == "__main__":
    print(example_monthly_snp_future_value(100,5))
    unittest.main()
