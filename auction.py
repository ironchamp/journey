#!/usr/bin/env python
# coding: utf-8

"""
    Purpose:
       Determine winning bidder and sale price to pay for a reserved-price item at the end of a sealed auction

    Rules:
        An item is for sale with a reserve price.
        We have several potential buyers, each one being able to place one or more bids.
        The buyer winning the auction is the one with the highest bid above or equal to the reserve price.
        The winning price is the highest bid price from a non-winning buyer above the reserve price
            (or the reserve price if none applies)

    Assumptions:
        The result can be determined statically, independent of the order or timing of the bids.
        All bids are in an exact number of Euros: no other currency nor cents may be added.
        Matching highest bids means that "subsequent" bidders are effectively ignored (arguably unfairly).
        The seller may bid on their own sale item, thereby increasing the reserve before the auction ends.
        The winning price does not account for any shipping or selling fee to effect the transaction.

    Usage:
        1. Create a JSON file (bids.json) containing all of the sale items and associated bids
        2. Execute main.py which loads sale items with bids, and governs the order of each sale

    Options:
        To investigate any failed tests, consider setting logging...level='DEBUG' (as now) for tracing
        Otherwise,

    Sample (debugged impact as if dynamic and in same order):
        A: 2 bids of 110 and 130 euros (=> A pays 100 reserve)
        B: 0 bids (=> no impact)
        C: 1 bid of 125 euros (=> A pays 125)
        D: 3 bids of 105, 115 and 90 euros (=> no impact)
        E: 3 bids of 132, 135 and 140 euros (=> E pays 130)
    Extra in 2nd similar sample:
        F: 1 bid of 136 euros (=> E pays 136)
"""

import json
import logging
# settings
logging.basicConfig(format='%(message)s', level='DEBUG')

# TODO: better to use config.py to hold sales lists/arrays instead of using "global" definitions within auction.py
# import config
# track array of reserve prices for unique sale items associated (many-to-one) with each seller
#   e.g. {'item': 'z', 'reserve': 250, 'seller': 'R'}, where reserve_price['z'] = 250  =>  {'z': 200}
reserve_price = {}

# TODO: perhaps better also to use NamedTuples imported from bisect module
# track flattened list of all bids, by bidding item related (one-to-many) with multiple bid prices from multiple bidders
#   e.g. [('z', 190, 'B'), ('z', 200, 'B'), ('z', 180, 'D')] => item, 'z' has 2 bids from bidder, 'B' & 1 bid from 'D'
all_bids: list[tuple[str, int, str]] = []


# clear all items for sale, including any bids
def clear_sales():
    global reserve_price
    reserve_price = {}
    global all_bids
    all_bids.clear()


# Import bids from JSON file to all_bids record dictionary
def load_sales(sales_file='bids.json'):
    with open(sales_file, 'r') as json_sales:
        sales = json.load(json_sales)
    # json_sales.close()
    for i in sales['sales']:
        SaleItem.sell(SaleItem(item=i['item'], reserve=i['reserve'], seller=i['seller']))
        for b in i['bids']:
            BidItem.bid(BidItem(item=i['item'], bid=b['bid'], bidder=b['bidder']))
    return sales


# Show all_bids record dictionary
def show_sales(sales):
    logging.debug(json.dumps(sales, indent=2))


class BidItem:
    def __init__(self, item: str, bid: int, bidder: str):
        self.item = item
        self.bid = bid
        self.bidder = bidder

    def bid(self):
        global all_bids
        all_bids.append((self.item, self.bid, self.bidder))

    def show(self):
        logging.debug(self.__dict__)


class SaleItem:
    def __init__(self, item: str, reserve: int, seller: str):
        self.item = item
        self.reserve = reserve
        self.seller = seller

    # values captured from JSON file
    def sell(self):
        global reserve_price
        reserve_price[self.item] = self.reserve

    def show(self):
        logging.debug(f"\n{self.__dict__}")

    def selling(self):
        global reserve_price
        global all_bids
        bidding_item = self.item
        better = reserve = reserve_price[bidding_item]
        self.show()
        # Assert exceptions if not loaded previously as expected
        try:
            # WARNING: expected matching seller not retained within dictionary of reserve prices per item
            assert self.seller != ''
            assert reserve == self.reserve
        except AssertionError:
            logging.error(f"\tMismatch of items (in main.py) with extracted sale items (from JSON file): {reserve_price}")

        # starting price is equivalent to the seller having bid on their own item, just below the reserve
        #   ...in whole euros (excluding cents)
        #   ...the seller is effectively the "winner" if there are no bids matching the reserve
        max_bid = reserve - 1
        price = 0
        winner = ''
        logging.debug(f"\tReserved price for '{bidding_item}' is {reserve}")

        # Filter out only bids for this item sale...
        """
        # No need to sort bids by price for algorithm, although typically may be prerequisite from a DB SQL query
        filtered_bidding = sorted([
            bidding for bidding in all_bids if bidding[0] == self.item and bidding[1] > 0],
                key=lambda bidding: bidding[1])
        """
        filtered_bidding = [bidding for bidding in all_bids if bidding[0] == self.item and bidding[1] > 0]
        logging.debug(filtered_bidding)

        # Determine winning bidder and item best sale price
        num_bids = 0
        for index, bidding in enumerate(filtered_bidding):
            item, bid, bidder = bidding
            # Assert exceptions if not filtered/queried previously as expected
            try:
                assert item == self.item
                assert bid > 0
                assert bidder != ''
            except AssertionError:
                logging.error(f"\tMismatch of items (in main.py) with extracted item bids (from JSON file): {bidding}")
            """
                Three main scenarios:
                1. if bid is highest bid so far:
                    if new winner, price set to previous better price (default reserve)
                    else record highest bid of current winner
                2. if bid higher than previous better price
                    if not the winner, price is same as bid price
                3. ignore bid if below reserve price (or better price so far)
            """
            if bid > max_bid:
                max_bid = bid
                if bidder != winner:
                    winner = bidder
                    price = better
                    logging.debug(f"\tNew winner {winner} increased €{price}")
                elif bid > price:
                    logging.debug(f"\tSame winner {winner} unchanged at €{price} (pending €{bid} possible)")
                better = bid
            elif bid > price:
                if bidder != winner:
                    price = bid
                    logging.debug(f"\tSame winner {winner} increased to €{price} (as offered by {bidder})")
            elif bid < better:
                logging.debug(f"\tNo impact from {bidder} because €{bid} is below the current €{better} price")
            num_bids = index + 1
        return winner, bidding_item, price, num_bids
