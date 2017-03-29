
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Input, Dense, LSTM, Dropout
from keras import backend as K

class DeepQNetwork:
    def __init__(
            self,
            n_actions,
            n_features,
            learning_rate=0.05,
            reward_decay=0.9,
            e_greedy=0.9,
            replace_target_iter=500,
            memory_size=500,
            batch_size=60,
            rnn_train_length = 20,
            e_greedy_increment=None,
            batchSize = 250,
            output_graph=False,
    ):
        self.batch_size = batch_size
        self.n_actions = n_actions
        self.n_features = n_features
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon_max = e_greedy
        self.replace_target_iter = replace_target_iter
        self.memory_size = memory_size
        self.rnn_train_length = rnn_train_length
        self.epsilon_increment = e_greedy_increment
        self.epsilon = 0 if e_greedy_increment is not None else self.epsilon_max

        # total learning step
        self.learn_step_counter = 0

        # initialize zero memory [s, a, r, s_]
        self.memory = pd.DataFrame(np.zeros((self.memory_size, n_features*2+2)))

        # consist of [target_net, evaluate_net]
        self._build_net()

        self.cost_his = []

    def my_init(self,shape, name=None):
        value = np.random.random(shape)
        return K.variable(value, name=name)

    def build_train_data(self):
        # sample batch memory from all memory
        X = np.ndarray(shape=(self.batch_size, self.rnn_train_length,self.n_features), dtype=float)
        X_ = np.ndarray(shape=(self.batch_size, self.rnn_train_length, self.n_features), dtype=float)
        for i in range(self.batch_size):
            X[i] = self.memory.iloc[i:i+self.rnn_train_length,:self.n_features].values
            X_[i] = self.memory.iloc[i:i+self.rnn_train_length,-self.n_features:].values
        s = self.memory.iloc[self.rnn_train_length -1:,:self.n_features].values
        s_ = self.memory.iloc[self.rnn_train_length -1:,-self.n_features:].values
        return X,X_,s,s_

    def _build_keras_net(self):
        model = Sequential()
        model.add(LSTM(50,
                       input_shape=(self.rnn_train_length, self.n_features)))
        #model.add(LSTM(30, input_dim=1))
        # model.add(Dropout(0.5))
        # model.add(LSTM(30, batch_input_shape=(20,3,1),stateful=True))
        # model.add(Dropout(0.4))
        model.add(Dense(self.n_actions,init="normal"))
        model.compile(optimizer='adam', loss='mse',metrics=['accuracy'])
        print(model.summary())
        return model

    def _build_net(self):
        # ------------------ build evaluate_net ------------------
        self.evaluate_net = self._build_keras_net()
        self.target_net = self._build_keras_net()


    def store_transition(self, s, a, r, s_):
        if not hasattr(self, 'memory_counter'):
            self.memory_counter = 0

        transition = np.hstack((s, [a, r], s_))
        # replace the old memory with new memory
        index = self.memory_counter % self.memory_size
        self.memory.iloc[index, :] = transition
        self.memory_counter += 1

    def choose_action(self, observation):
        # to have batch dimension when feed into tf placeholder
        observation = observation[np.newaxis, :]
        if np.random.uniform() < self.epsilon and self.memory_counter >= self.rnn_train_length:
            # forward feed the observation and get q value for every actions
            x = self.memory.iloc[-self.rnn_train_length:, :self.n_features].values
            x = x.reshape(1, self.rnn_train_length, self.n_features)
            actions_value =  self.evaluate_net.predict(x)
            action = np.argmax(actions_value)
        else:
            action = np.random.randint(0, self.n_actions)
        return action

    def _replace_target_params(self):
        self.evaluate_net.save_weights("tempWeights.h5")
        self.target_net.load_weights("tempWeights.h5")

    def learn(self):
        # check to replace target parameters
        if self.learn_step_counter % self.replace_target_iter == 0:
            self._replace_target_params()
            print('\ntarget_params_replaced\n')

        X,X_,s,s_ = self.build_train_data()

        #
        #当前状态的input序列在memory里，那下一个状态的input序列在哪里
        q_next = self.target_net.predict(X_)
        q_eval = self.evaluate_net.predict(X)

        q_target = q_eval.copy()

        batch_index = np.arange(self.batch_size, dtype=np.int32)
        eval_act_index = self.memory.values[self.rnn_train_length-1:, self.n_features].astype(int)
        reward = self.memory.values[self.rnn_train_length-1:, self.n_features + 1]

        q_target[batch_index, eval_act_index] = reward + self.gamma * np.max(q_next, axis=1)

        # train eval network
        history = self.evaluate_net.fit(X,q_target,
                nb_epoch=1,
                shuffle=False,
                verbose=0)

        self.cost_his.append(history.history['loss'])

        # increasing epsilon
        self.epsilon = self.epsilon + self.epsilon_increment if self.epsilon < self.epsilon_max else self.epsilon_max
        #print(self.epsilon)
        self.learn_step_counter += 1


    def plot_cost(self):
        import matplotlib.pyplot as plt
        plt.plot(np.arange(len(self.cost_his)), self.cost_his)
        plt.show()
