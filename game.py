import json
import random
from collections import deque

import numpy as np


class Reward(object):
    """
    this is a class for storing and update delayed reward
    """
    def __init__(self, value=None):
        self.value = value  # this would be the actual value of the reward

    def add(self, value):
        """
        add the value of the current reward

        :param value:
        :return:
        """
        self.value += value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class Account(object):
    """
    this class is for managing the cash and position info.
    it keeps track of the cash amount, of the size of the positions and of cost of the positions,
    and updates the corresponding rewards when a position is sold
    """
    def __init__(self, initial_cash, transaction_fee=0):
        self.cash = initial_cash  # available cash

        self.queue = deque()  # the queue for storing the positions
        self.position_size = 0  # size of all positions

        self.transactions_fee = transaction_fee

    def buy(self, buying_amount, buying_price):
        """
        buy stocks.
        update the queue according to the input info.

        :param buying_amount:
        :param buying_price:
        :param reward_obj:

        :return: the reward object
        """
        cost = buying_amount * buying_price + self.transactions_fee

        if cost <= self.cash:
            self.cash -= cost
            self.position_size += buying_amount
            reward = Reward(-self.transactions_fee)
            self.queue.appendleft((buying_amount, buying_price, reward))

            return reward
        else:
            return Reward(0)

    def sell(self, selling_amount, selling_price):
        """
        sell stocks.
        update the queue according to the input info.

        :param selling_amount:
        :param selling_price:
        :param reward_obj:

        :return: the reward object
        """
        assert selling_amount > 0

        if self.position_size > 0:  # there are stocks to sell
            if selling_amount > self.position_size:
                selling_amount = self.position_size  # can't sell more than the size of current position

            selling_reward = Reward(-self.transactions_fee)
            self.cash -= self.transactions_fee

            while selling_amount > 0:
                buying_amount, buying_price, buying_reward = self.queue.pop()

                effective_amount = min(buying_amount, selling_amount)  # actual selling amount for this long position
                income = (selling_price - buying_price) * effective_amount  # cash income before fee
                buying_reward.add(income / 2)  # update rewards
                selling_reward.add(income / 2)

                self.cash += selling_price * effective_amount  # update cash
                self.position_size -= effective_amount  # update position

                if selling_amount < buying_amount:  # some of the long position left, push back to queue
                    self.queue.append((buying_amount-selling_amount, buying_price, buying_reward))

                selling_amount -= effective_amount  # how many left to sell

            return selling_reward

        else:
            return Reward(0)

    def liquidate_positions(self, selling_price):
        """
        liquidate all the positions.
        happens at the very end of games.

        :param selling_price:
        :return:
        """
        if self.queue:
            self.sell(self.position_size, selling_price)

    def get_net_value(self, market_price):
        return self.cash + self.position_size * market_price


class Game(object):
    """

    """
    def __init__(self, game_length, initial_cash, trading_amount, max_loss, transaction_fee):
        """
        ALL games starts with stock price equals 1

        :param game_length: number of trading days in a game
        :param initial_cash: amount of cash to start with
        :param trading_amount: number of stocks to buy or sell each time
        :param max_loss: maximum loss (for example, 0.3 means when the loss reaches 30% of the initial cash, game ends)
        """
        with open('companies.json') as file:  # read companies.json
            companies = json.load(file)
        self.companies = [company['Symbol'] for company in companies]  # store all the company symbols

        self.game_length = game_length
        self.initial_cash = initial_cash
        self.trading_amount = trading_amount
        self.max_loss = max_loss
        self.transaction_fee = transaction_fee

        self.observations = None
        self.prices = None
        self.net_values = None
        self.pointer = 0

        self.account = Account(self.initial_cash, self.transaction_fee)

    def render(self):
        pass

    def reset(self):
        raw_data = None
        while True:
            company = random.choice(self.companies)  # randomly select a company
            with open('prices/{}.json'.format(company)) as file:
                raw_data = json.load(file)  # read price data of this company

            if len(raw_data) > self.game_length:  # break if this company has a history longer than the game_length
                break

        # randomly pick a start date
        start = random.randint(0, len(raw_data) - self.game_length - 1)

        # pre-allocate memory
        self.observations = np.zeros((self.game_length, 4), dtype=np.float64)
        self.prices = np.zeros((self.game_length, 4), dtype=np.float64)

        # close price of the day before the first day of the game, used to normalize price to 1
        price_0 = float(raw_data[start]['Adj_Close'])

        # iterate through the records
        for i in range(self.game_length):
            record = raw_data[i + start + 1]
            pre_close = float(raw_data[i + start]['Adj_Close'])  # previous adjusted close

            #这里会出错
            try:
                adjust = float(record['Adj_Close']) / float(record['Close'])
            except:
                continue

            raw_prices = np.array([float(record['Open']),
                                   float(record['High']),
                                   float(record['Low']),
                                   float(record['Close'])])

            self.observations[i, :] = raw_prices * adjust / pre_close - 1
            self.prices[i, :] = raw_prices * adjust / price_0

        # reset
        self.pointer = 0
        self.cash = self.initial_cash
        self.position = 0
        self.net_values = [self.cash]

        self.account = Account(self.initial_cash, self.transaction_fee)

        return self.observations[0, :]

    def step(self, action):
        """

        :param action: 0 - buy_at_open; 1 - sell_at_open; 2 - do_nothing
        :return: new_observation, reward, done, info
        """
        self.pointer += 1
        open_price, high_price, low_price, close_price = self.prices[self.pointer]  # get prices

        if action == 0:  # buy at open
            reward = self.account.buy(self.trading_amount, open_price)
        elif action == 1:  # sell at open
            reward = self.account.sell(self.trading_amount, open_price)
        elif action == 2:  # do nothing
            reward = Reward(0)
        else:
            raise ValueError('action must be 0, 1 or 2')

        # new observation
        new_observation = self.observations[self.pointer]

        # check if game over
        end_of_game = (self.pointer == self.game_length - 1)
        lost_too_much = self.account.get_net_value(low_price) < self.initial_cash * (1 - self.max_loss)
        done = end_of_game or lost_too_much

        if end_of_game:
            self.account.liquidate_positions(close_price)
        if lost_too_much:
            self.account.liquidate_positions(low_price)

        # save net_value
        net_value = self.account.get_net_value(close_price)
        self.net_values.append(net_value)

        # new info
        info = {}

        return new_observation, reward, done, info


def main():
    rewards = []

    g = Game(game_length=250,
             initial_cash=10000,
             trading_amount=50,
             max_loss=0.3,
             transaction_fee=10)
    obs = g.reset()

    buy = 0
    sell = 1
    wait = 2

    new_observation, reward, done, info = g.step(buy)
    rewards.append(reward)

    new_observation, reward, done, info = g.step(buy)
    rewards.append(reward)

    new_observation, reward, done, info = g.step(sell)
    rewards.append(reward)

    new_observation, reward, done, info = g.step(sell)
    rewards.append(reward)

    print(rewards)


if __name__ == '__main__':
    main()
