from collections import deque
import json
import random

import numpy as np


class Reward(object):
    """
    this is a class for storing and computing delayed reward
    """
    def __init__(self, value=None):
        self._value = value  # this would be the actual value of the reward

        self._cost = 0  # cost of this position
        self._payoff = 0  # payoff of this position when sold

        self._remaining_amount = 0  # remaining amount to be covered

    @property
    def value(self):
        """
        the actual value of the delayed reward
        """
        if self._value is not None:  # if already computed the reward
            return self._value
        else:  # never computed before
            if self._remaining_amount == 0:  # no more position to be covered
                self._value = ((self._payoff / self._cost) - 1) * 10  # compute reward
                return self._value
            else:
                raise ValueError('Remaining Position must be 0 when computing reward')  # raise error

    def buy(self, buying_amount, buying_price, transaction_fee):
        """

        :param buying_amount:
        :param buying_price:
        :param transaction_fee: only buying reward need to compute transaction fee
        :return:
        """
        self._remaining_amount += buying_amount
        self._cost += buying_amount * buying_price + transaction_fee

    def sell(self, selling_amount, selling_price, transaction_fee):
        """

        :param selling_amount:
        :param selling_price:
        :param transaction_fee: only selling reward need to compute transaction fee
        :return:
        """
        self._remaining_amount -= selling_amount
        self._payoff += selling_amount * selling_price - transaction_fee

    def __str__(self):
        return 'Reward({})'.format(self._value if self._value is not None else 'N/A')

    def __repr__(self):
        return self.__str__()


class Account(object):
    """
    this class is for managing the cash and position info.
    it keeps track of the cash amount, of the size of the positions and of cost of the positions,
    and updates the corresponding rewards when a position is sold
    """
    def __init__(self, initial_cash, transaction_fee=0):
        self.cash = initial_cash  # available cash
        self.position_size = 0  # size of all positions
        self.queue = deque()  # the queue for storing the positions

        self.transactions_fee = transaction_fee  # fixed amount transaction fee

    def buy(self, buying_amount, buying_price):
        """
        buy stocks.

        :return: the reward object
        """
        buying_cost = buying_amount * buying_price + self.transactions_fee  # cash needed for this buy

        if buying_cost <= self.cash:  # has enough cash
            self.cash -= buying_cost
            self.position_size += buying_amount

            reward = Reward()
            reward.buy(buying_amount, buying_price, self.transactions_fee)  # update reward

            self.queue.appendleft((buying_amount, buying_price, reward))

            return reward
        else:  # not enough cash
            return Reward(0)

    def sell(self, selling_amount, selling_price):
        """
        sell stocks.

        :return: the reward object
        """
        if self.position_size > 0:  # have stocks to sell
            if selling_amount > self.position_size:
                selling_amount = self.position_size  # can't sell more than the size of current position

            total_selling_amount = selling_amount  # save the total selling amount

            selling_reward = Reward()
            selling_reward.sell(selling_amount, selling_price, self.transactions_fee)

            self.cash -= self.transactions_fee

            # sell stocks in FIFO order
            while selling_amount > 0:
                buying_amount, buying_price, buying_reward = self.queue.pop()

                effective_amount = min(buying_amount, selling_amount)  # actual selling amount for this buying order
                self.cash += (selling_price - buying_price) * effective_amount
                self.position_size -= effective_amount

                buying_reward.sell(effective_amount, selling_price, 0)  # not counting selling fees in buying reward
                selling_reward.buy(effective_amount, buying_price, 0)  # not counting buying fees in selling reward

                if effective_amount < buying_amount:  # some of the long position left, push back to queue
                    self.queue.append((buying_amount-effective_amount, buying_price, buying_reward))

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
        """
        get the net value of the entire position.

        :param market_price: the price at which the position would be evaluated
        :return:
        """
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
        :param transaction_fee: fixed amount transaction fee
        """
        # with open('companies.json') as file:  # read companies.json
        #     companies = json.load(file)
        # self.companies = [company['Symbol'] for company in companies]  # store all the company symbols

        self.companies = ['AAON']

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
        """
        re-start a new game

        :return: the first observation of the new game
        """
        # choose a company and load the data
        raw_data = None
        while True:
            company = random.choice(self.companies)  # randomly select a company
            with open('prices/{}.json'.format(company)) as file:
                raw_data = json.load(file)  # read price data of this company

            if len(raw_data) > self.game_length:  # this company has a history longer than the game_length
                break

        # randomly pick a start date, first day of the game
        # random.randint: Return a random integer N such that a <= N <= b.
        # start = random.randint(1, len(raw_data) - self.game_length)
        start = 100

        # pre-allocate memory
        self.observations = np.zeros((self.game_length, 4), dtype=np.float64)
        self.prices = np.zeros((self.game_length, 4), dtype=np.float64)

        # close price of the day before the first day of the game, used to normalize price to 1
        price_0 = float(raw_data[start-1]['Adj_Close'])

        # iterate through the records
        for i in range(self.game_length):
            record = raw_data[i + start]
            pre_close = float(raw_data[i + start - 1]['Adj_Close'])  # previous adjusted close

            adjust = float(record['Adj_Close']) / float(record['Close'])  # coefficient to adjust prices

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

        # new observation and new price
        new_observation = self.observations[self.pointer]
        open_price, high_price, low_price, close_price = self.prices[self.pointer]  # get prices

        if action == 0:  # buy at open
            reward = self.account.buy(self.trading_amount, open_price)
        elif action == 1:  # sell at open
            reward = self.account.sell(self.trading_amount, open_price)
        elif action == 2:  # do nothing
            reward = Reward(0)
        else:
            raise ValueError('action must be 0, 1 or 2')

        # check if game over
        end_of_game = (self.pointer == self.game_length - 1)
        lost_too_much = self.account.get_net_value(low_price) < (self.initial_cash * (1 - self.max_loss))
        done = end_of_game or lost_too_much

        if end_of_game:
            self.account.liquidate_positions(close_price)
        elif lost_too_much:
            self.account.liquidate_positions(low_price)

        # save net_value
        net_value = self.account.get_net_value(close_price)
        self.net_values.append(net_value)

        # new info
        info = {'cash': self.account.cash,
                'positions': self.account.position_size,
                'net_value': net_value,
                'prices': (open_price, high_price, low_price, close_price)}

        return new_observation, reward, done, info


def main():
    g = Game(game_length=250,
             initial_cash=10000,
             trading_amount=50,
             max_loss=0.3,
             transaction_fee=1)
    obs = g.reset()

    buy = 0
    sell = 1
    wait = 2

    rewards = []

    new_observation, reward, done, info = g.step(buy)
    rewards.append(reward)

    new_observation, reward, done, info = g.step(buy)
    rewards.append(reward)

    new_observation, reward, done, info = g.step(sell)
    rewards.append(reward)

    new_observation, reward, done, info = g.step(sell)
    rewards.append(reward)

    print([r.value for r in rewards])


if __name__ == '__main__':
    main()
