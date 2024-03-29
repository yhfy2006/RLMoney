
import numpy as np
from collections import deque
import matplotlib.pyplot as plt
import time
import sys, getopt
import statistics


class Evaluator(object):

    def __init__(self,deque_window=400,initial_cash = 10000,write_to_file=False,data_file = 'data/dataLog',print_data_log = True,log_all_netvalues = False):
        self.net_values_list = []
        self.net_stdev_list =[]
        self.cash_list = []
        self.game_cicles_list = []
        self.postion_list = []
        self.q_netValue = deque(maxlen=deque_window)
        self.history_loss = []
        self.write_to_file = write_to_file
        self.print_data = print_data_log
        self.data_file = data_file
        self.log_all_netvalues = log_all_netvalues
        self.initial_cash =initial_cash



    def update(self,net_value,net_stdev,cash,game_cicle,position):
        if float(net_stdev) == 0:
            return
        self.net_values_list.append(net_value)
        self.net_stdev_list.append(net_stdev)
        self.cash_list.append(cash)
        self.game_cicles_list.append(game_cicle)
        self.postion_list.append(position)
        if self.write_to_file:
            self.append_date_to_file(net_value,cash,game_cicle,position,net_stdev)

    def sharpe_ratio(self):
        return_value = [(i-self.initial_cash)/float(self.initial_cash) for i in self.net_values_list]
        return_value_std = self.net_stdev_list
        ratio = [return_value[i]/float(return_value_std[i]) for i in range(len(return_value))]
        return ratio

    def std_netvalues(self,value_list):
        head = self.initial_cash
        shifted_values = []
        for i in range(len(value_list)):
            value = (value_list[i]-head)/float(value_list[i])
            shifted_values.append(value)
        return statistics.stdev(shifted_values)

    def overall_avg(self):
        result = []
        cache = []
        for net_value in self.net_values_list:
            # net_values is a list
            cache.append(net_value)
            result.append( sum(cache)/float(len(cache)) )
        return result

    def deque_avg(self):
        self.q_netValue.clear()
        result = []
        for net_value in self.net_values_list:
            self.q_netValue.append(net_value)
            avg = sum(self.q_netValue)/float(len(self.q_netValue))
            result.append(avg)
        return result

    def deque_mid(self):
        self.q_netValue.clear()
        result = []
        for net_value in self.net_values_list:
            self.q_netValue.append(net_value)
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

    def append_date_to_file(self,net_value,cash,game_cicle,position,net_std):
        outStr = str(net_value)+","+str(cash)+","+str(game_cicle)+","+str(position)+","+str(net_std)
        index = len(self.net_values_list)
        if self.print_data:
            print(str(index)+"===>"+outStr)
        with open(self.data_file+".csv", 'a') as file:
            file.write(outStr)
            file.write('\n')

        # if self.log_all_netvalues:
        #     with open(self.data_file+"_netvalues.csv", 'a') as fp:
        #         for net_value in net_value:
        #             fp.write(str(index)+","+str(net_value))
        #             fp.write('\n')




    def _clear_data(self):
        self.net_values_list.clear()
        self.cash_list.clear()
        self.game_cicles_list.clear()
        self.postion_list.clear()
        self.q_netValue.clear()
        self.history_loss.clear()
        self.net_stdev_list.clear()


    def load_from_data(self):
        self._clear_data()
        temp_write_to_file = self.write_to_file
        self.write_to_file = False
        with open(self.data_file+".csv") as fp:
            for line in fp:
                values = line.split(",")
                net_value = float(values[0])
                cash = float(values[1])
                game_cicle = float(values[2])
                position = float(values[3])
                net_std =float(values[4])
                self.update(net_value,cash,game_cicle,position,net_std)

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
    eval = Evaluator(data_file='data/dataLog_4_4_2017')
    eval.load_from_data()
    if option == 'ov_avg':
        eval.plot(eval.overall_avg())
    if option == 'dq_avg':
        eval.plot(eval.deque_avg())
    if option == 'exp_avg':
        eval.plot(eval.exp_moving_avg())
    if option == 'dq_mid':
        eval.plot(eval.deque_mid())
    if option == 'sp_rio':
        eval.plot(eval.sharpe_ratio())



def main(argv):
   try:
      opts, args = getopt.getopt(argv,"r:l:",["ov_avg","dq_avg","dq_mid","exp_avg"])
   except getopt.GetoptError:
      print ('usage: dqn_eval.py -r(print)|-l(plot) ov_avg|dq_avg|exp_avg|dq_mid|sp_rio')
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
          if arg == 'sp_rio':
              plot_d('sp_rio')

if __name__ == '__main__':
    main(sys.argv[1:])
