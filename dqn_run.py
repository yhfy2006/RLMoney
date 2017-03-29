__author__ = 'chhe'

from game import Game
from dqn_brain import DeepQNetwork
import matplotlib.pyplot as plt



def run_network():
    step = 0
    gameRun = 0
    for episode in range(500000):
        gameRun += 1
        observation = env.reset()

        gameCicle = 0
        while True:
            step += 1
            gameCicle += 1
            action = RL.choose_action(observation)

            observation_,reward,done,info = env.step(action)

            RL.store_transition(observation,action,reward,observation_)

            if step % memory_size == 0:
                RL.learn()
            observation = observation_

            # plt.axis([0, gameSize, 0, 10000])
            # plt.scatter(gameSize, env.cash)
            # plt.pause(0.05)
            #plt.plot(x, y1, color='red', linewidth=1.0, linestyle='--')

            if done:
                print(str(env.cash)+" game:"+str(gameRun)+" used steps:"+str(gameCicle))
                RL.memory_counter = 0
                break




if __name__ == "__main__":

    gameSize = 250

    env = Game(gameSize, 10000, 50, 0.3)
    n_actions = 3
    n_features =4

    rnn_train_length = 20
    train_batch_size = 10
    memory_size = rnn_train_length + train_batch_size - 1

    RL = DeepQNetwork(n_actions, n_features,
                      learning_rate=0.03,
                      reward_decay=0.7,
                      e_greedy=0.9,
                      replace_target_iter=200,
                      memory_size=memory_size,
                      e_greedy_increment = 0.001,
                      rnn_train_length = rnn_train_length,
                      batch_size = train_batch_size,
                      load_weight=False
                      )
    run_network()
