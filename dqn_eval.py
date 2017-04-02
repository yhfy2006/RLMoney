
import numpy as np
from collections import deque
import matplotlib.pyplot as plt


class Evaluator(object):

    def __init__(self,deque_window=1500,write_to_file=False,data_file = 'dataLog.csv',print_data_log = True):
        self.net_values_list = []
        self.cash_list = []
        self.game_cicles_list = []
        self.postion_list = []
        self.q_netValue = deque(maxlen=deque_window)
        self.history_loss = []
        self.write_to_file = write_to_file
        self.print_data = print_data_log
        self.data_file = data_file



    def update(self,net_value,cash,game_cicle,position):
        self.net_values_list.append(net_value)
        self.cash_list.append(cash)
        self.game_cicles_list.append(game_cicle)
        self.postion_list.append(position)
        if self.write_to_file:
            self.append_date_to_file(net_value,cash,game_cicle,position)

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

    def exp_moving_avg(self):
        que_sum = 0
        discount = 0.99
        ema = []
        vals = []
        for val in self.net_values_list:
            if val < 50000:
                    que_sum *= discount
                    que_sum += (1 - discount) * val
                    ema.append(que_sum)
                    vals.append(val)
        return vals

        # ax1 = plt.subplot('121')
        # ax2 = plt.subplot('122')
        #
        # ax1.plot(ema)
        # ax1.grid(True)
        # ax2.plot(vals)
        # ax2.grid(True)
        #
        # plt.show()

    def append_date_to_file(self,net_value,cash,game_cicle,position):
        outStr = str(net_value)+","+str(cash)+","+str(game_cicle)+","+str(position)
        if self.print_data:
            print(str(len(self.net_values_list))+"===>"+outStr)
        with open(self.data_file, 'a') as file:
            file.write(outStr)
            file.write('\n')



    def _clear_data(self):
        self.net_values_list.clear()
        self.cash_list.clear()
        self.game_cicles_list.clear()
        self.postion_list.clear()
        self.q_netValue.clear()
        self.history_loss.clear()


    def load_from_data(self):
        temp_write_to_file = self.write_to_file
        self.write_to_file = False
        with open(self.data_file) as fp:
            for line in fp:
                values = line.split(",")
                net_value = float(values[0])
                cash = float(values[1])
                game_cicle = float(values[2])
                position = float(values[3])
                self.update(net_value,cash,game_cicle,position)

        self.write_to_file = temp_write_to_file



if __name__ == '__main__':

    eval = Evaluator()

    with open('netValue.txt') as fp:
        logLines = 0
        x = []
        for line in fp:
            logLines += 1
            x.append(logLines)
            net_value = float(line)
            eval.update(net_value,0,0,0)

    #splt.plot(eval.overall_avg())
    plt.plot(eval.deque_avg())
    plt.show()
   # print(eval.deque_avg())