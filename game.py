import json
import random

import numpy as np


class Game(object):
    """

    """
    def __init__(self, game_length, initial_cash, trading_amount, max_loss):
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

        self.observations = None
        self.prices = None
        self.net_values = None
        self.pointer = 0
        self.cash = 0
        self.position = 0

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
            adjust = float(record['Adj_Close']) / float(record['Close'])
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

        return self.observations[0, :]

    def step(self, action):
        """

        :param action: 0 - buy_at_open; 1 - sell_at_open; 2 - do_nothing
        :return: new_observation, reward, done, info
        """
        self.pointer += 1
        open_price, high_price, low_price, close_price = self.prices[self.pointer]  # get prices

        if action == 0:  # buy at open
            cost = open_price * self.trading_amount
            if cost <= self.cash:  # has sufficient funds
                self.position += self.trading_amount
                self.cash -= cost
        elif action == 1:  # sell at open
            if self.position >= self.trading_amount:
                self.position -= self.trading_amount
                self.cash += open_price * self.trading_amount
        elif action == 2:  # do nothing
            pass
        else:
            raise ValueError('action must be 0, 1 or 2')

        # new observation
        new_observation = self.observations[self.pointer]

        # new net_value and new reward
        net_value = self.cash + self.position * close_price
        reward = net_value - self.net_values[-1]
        self.net_values.append(net_value)

        # check if game over
        end_of_game = (self.pointer == self.game_length - 1)
        lost_too_much = (self.cash + self.position * low_price) < self.initial_cash * (1 - self.max_loss)
        done = end_of_game or lost_too_much

        # new info
        info = {}

        return new_observation, reward, done, info


def main():
    g = Game(250, 100, 5, 0.3)
    obs = g.reset()

    buy = 0
    sell = 1
    wait = 2

    new_observation, reward, done, info = g.step(buy)


if __name__ == '__main__':
    main()
