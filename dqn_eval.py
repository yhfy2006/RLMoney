
import numpy as np
from collections import deque
import matplotlib.pyplot as plt


class Evaluator(object):



    def __init__(self,deque_window=1500):
        self.net_values_list = []
        self.cash_list = []
        self.game_cicles_list = []
        self.q_netValue = deque(maxlen=deque_window)


    def update(self,net_values,cash,game_cicle):
        self.net_values_list.append(net_values)
        self.cash_list.append(cash)
        self.game_cicles_list.append(game_cicle)

    def overall_avg(self):
        result = []
        cache = []
        for i in self.net_values_list:
            cache.append(i)
            result.append( sum(cache)/float(len(cache)) )
        return result

    def deque_avg(self):
        self.q_netValue.clear()
        result = []
        for i in self.net_values_list:
            self.q_netValue.append(i)
            avg = sum(self.q_netValue)/float(len(self.q_netValue))
            result.append(avg)
        return result


        return
if __name__ == '__main__':

    eval = Evaluator()

    with open('netValue.txt') as fp:
        logLines = 0
        x = []
        for line in fp:
            logLines += 1
            x.append(logLines)
            net_value = float(line)
            eval.update(net_value,0,0)

    #splt.plot(eval.overall_avg())
    plt.plot(eval.deque_avg())
    plt.show()
   # print(eval.deque_avg())