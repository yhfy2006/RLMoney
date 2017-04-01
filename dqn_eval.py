
import numpy as np

class Evaluator(object):



    def __init__(self,deque_window=200):
        self.net_values_list = []
        self.cash_list = []
        self.game_cicles_list = []
        self.deque_window = deque_window


    def update(self,net_values,cash,game_cicle):
        self.net_values_list.append(net_values)
        self.cash_list.append(cash)
        self.game_cicles_list.append(game_cicle)

    def deque_avg(self):

        return
