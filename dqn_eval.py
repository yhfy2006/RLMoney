
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
import time
import sys, getopt
import statistics


class Evaluator(object):

    def __init__(self,deque_window=400,write_to_file=False,data_file = 'dataLog.csv',print_data_log = True):
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

    def sharpe_ratio(self):
        return_value = [(i-10000)/float(10000) for i in self.net_values_list]
        return_value_std = []

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

    def deque_mid(self):
        self.q_netValue.clear()
        result = []
        for i in self.net_values_list:
            self.q_netValue.append(i)
            avg = statistics.median(self.q_netValue)
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
        return ema

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
        self._clear_data()
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

    def plot(self,data):
        plt.plot(data)
        plt.show()


def print_d(option):
    eval = Evaluator()
    while(True):
        eval.load_from_data()
        if option == 'ov_avg':
            print(eval.overall_avg()[-1])
        if option == 'dq_avg':
            print(eval.deque_avg()[-1])
        if option == 'exp_avg':
            print(eval.exp_moving_avg()[-1])
        if option == 'dq_mid':
            print(eval.deque_mid()[-1])
        time.sleep(6)

def plot_d(option):
    eval = Evaluator()
    eval.load_from_data()
    if option == 'ov_avg':
        eval.plot(eval.overall_avg())
    if option == 'dq_avg':
        eval.plot(eval.deque_avg())
    if option == 'exp_avg':
        eval.plot(eval.exp_moving_avg())
    if option == 'dq_mid':
        eval.plot(eval.deque_mid())



def main(argv):
   try:
      opts, args = getopt.getopt(argv,"r:l:",["ov_avg","dq_avg","dq_mid","exp_avg"])
   except getopt.GetoptError:
      print ('usage: dqn_eval.py -r(print)|-l(plot) ov_avg|dq_avg|exp_avg|dq_mid')
      sys.exit(2)

   for opt, arg in opts:
      if opt == '-h':
         print ('dqn_eval.py -r(print)|-l(plot) ov_avg|dq_avg|exp_avg|dq_mid')
         print ('ov_avg = overall_ avg')
         print ('dq_avg = deque_ avg')
         print ('exp_avg = exp_moving_avg')
         print ('dq_mid = deque_median')
         sys.exit()
      if opt == '-r':
          if arg == 'ov_avg':
              print_d('ov_avg')
          if arg == 'dq_avg':
              print_d('dq_avg')
          if arg == 'exp_avg':
              print_d('exp_avg')
          if arg == 'dq_mid':
              print_d('dq_mid')

      if opt == '-l':
          if arg == 'ov_avg':
              plot_d('ov_avg')
          if arg == 'dq_avg':
              plot_d('dq_avg')
          if arg == 'exp_avg':
              plot_d('exp_avg')
          if arg == 'dq_mid':
              plot_d('dq_mid')

if __name__ == '__main__':
    main(sys.argv[1:])
