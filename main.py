#!/usr/bin/env python
# coding: utf-8

from auction import SaleItem
# from auction import BidItem
import auction
# TODO: better to use config.py to hold sales lists/arrays instead of using "global" definitions within auction.py
# import config

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    auction.clear_sales()
    all_sales = auction.load_sales('bids.json')
    auction.show_sales(all_sales)

    # NOTE: order of test cases here may differ from that in loaded JSON file
    #   ...essentially used as key indices matching associated bids from the JSON file
    sales = [
        ('1a', SaleItem(item='x', reserve=100, seller='P')),
        ('1b', SaleItem(item='xx', reserve=100, seller='P')),
        ('2', SaleItem(item='y', reserve=150, seller='Q')),
        ('3', SaleItem(item='z', reserve=250, seller='R'))
    ]
    print()
    for test_num, sale in sales:
        print(f"Test case {test_num}:")
        winner, item, price, num = SaleItem.selling(sale)
        if price >= sale.reserve:
            print(f"\tWinner of item, '{item}' (from {sale.seller}) is {winner} at €{price} (after {num} bids)")
        else:
            print(f"\tUnsold item, '{item}' (from {sale.seller}) since all {num} bids below reserve (€{sale.reserve})")
    print()