__author__ = 'chhe'

from game import Game
from dqn_brain import DeepQNetwork
from dqn_eval import Evaluator


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
                evaluator.history_loss = RL.currentLoss

            observation = observation_

            if done:
                evaluator.update(env.net_values[-1],env.cash,gameCicle,env.position)
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
                      replace_target_iter=100,
                      memory_size=memory_size,
                      e_greedy_increment = 0.001,
                      rnn_train_length = rnn_train_length,
                      batch_size = train_batch_size,
                      load_weight=False
                      )

    evaluator = Evaluator(write_to_file=True)

    run_network()
