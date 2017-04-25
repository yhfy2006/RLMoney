__author__ = 'chhe'

from game import Game
from dqn_brain import DeepQNetwork
from dqn_eval import Evaluator


def run_network():
    step = 0

    for episode in range(9000):
        observation = env.reset()

        gameCicle = 0
        while True:
            step += 1
            gameCicle += 1

            if env.pointer < rnn_train_length - 1:
                action = RL.choose_action(None)
            else:
                obs = env.observations[env.pointer-rnn_train_length+1:env.pointer+1]
                action = RL.choose_action(obs)

            observation_,reward,done,info = env.step(action)
            RL.store_history(observation,action,reward,observation_)

            observation = observation_

            if done:
                RL.learn_on_history()
                net_stdev =evaluator.std_netvalues(env.net_values)
                print("game:",episode,info['net_value'],info['cash'],net_stdev,gameCicle,info['positions'])
                evaluator.update(info['net_value'],info['cash'],net_stdev,gameCicle,info['positions'])
                RL.memory_counter = 0
                RL.reset_data_record()
                break



if __name__ == "__main__":

    gameSize = 250
    initial_cash =10000

    env = Game(gameSize, initial_cash, 50, 0.3,transaction_fee=1)
    n_actions = 3
    n_features =4

    rnn_train_length = 30
    train_batch_size = 20

    RL = DeepQNetwork(n_actions, n_features,
                      learning_rate=0.03,
                      reward_decay=0.7,
                      e_greedy=0.9,
                      replace_target_iter=50,
                      e_greedy_increment = 0.005,
                      rnn_train_length = rnn_train_length,
                      batch_size = train_batch_size,
                      load_weight=False
                      )

    evaluator = Evaluator(write_to_file=True,print_data_log=False,initial_cash=initial_cash)

    run_network()
