import json
import random


class Game(object):
    """

    """
    def __init__(self):
        with open('companies.json') as file:
            companies = json.load(file)
        self.companies = [company['Symbol'] for company in companies]

        self.game_length = 250  # number of trading days in a game

    def render(self):
        pass

    def reset(self):
        while True:
            company = random.choice(self.companies)  # randomly select a company
            with open('prices/{}.json'.format(company)) as file:
                raw_data = json.load(file)  # read price data of this company

            if len(raw_data) > self.game_length:  # break if this company has a history longer than the game_length
                break

        # randomly pick a start date

        

    def step(self, action):
        pass


def main():
    g = Game()
    g.reset()


if __name__ == '__main__':
    main()
