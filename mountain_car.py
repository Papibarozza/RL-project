import gym
from keras.optimizers import Adam
from keras.models import Sequential
from keras.layers import Dense, Activation
import numpy as np
env = gym.make('CartPole-v0')
class Transition(object):
  s_curr = None
  a = None
  r_t = None
  s_next= None
  def __init__(self,s_curr,a,r,s_next):
    self.s_curr=s_curr
    self.a = a
    self.r = r
    self.s_next = s_next

nb_actions = env.action_space.n
model = Sequential([
    Dense(16,input_dim=4),
    Activation('relu'),
    Dense(nb_actions),
    Activation('linear')
])

Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, amsgrad=False)
model.compile(loss='mean_squared_error',
              optimizer='adam',
              metrics=['accuracy'])
epsilon = 0.3
gamma = 0.2


replay_memory = set()
#for i in range(1,1000):
  #replay_memory.add(Transition(np.random.rand(1,4),np.random.randint(0,1),0.1,np.random.rand(1,4)))

for i_episode in range(10000):
    observation = env.reset()
    
    for t in range(200):
        #env.render()
        best_action = env.action_space.sample() if (np.random.random() < epsilon) else np.argmax(model.predict(np.array([observation]))) #Runs the state and all actions through network and returns best.
        new_observation, reward, done, info = env.step(best_action)
        #print(new_observation)
        replay_memory.add(Transition(observation,best_action,reward,new_observation))
        observation = new_observation       
        if done:
            #print("Episode finished after {} timesteps".format(t+1))
            #print(len(replay_memory))
            break

    if(len(replay_memory) > 2000 and i_episode%1000 == 0):
      print('Updating model..')
      X_replay = np.zeros([500,4])
      Y_replay = np.zeros([500,2])
      for i in range(1,500):
          replay = replay_memory.pop()
          #print(replay.s_curr)
          X_replay[i,:] = replay.s_curr

          q_vals = model.predict(np.array([replay.s_next]))
          followup_best_action = np.argmax(q_vals) #Which action gives best value given the next state

          Y_replay[i,:] = [0,0] #Set both to zero first
          Y_replay[i,followup_best_action] = replay.r+gamma*q_vals[0][followup_best_action] #Then update the Q-value for the best action

      model.fit(X_replay,Y_replay,epochs=1,batch_size=500) #Model is updated
      

    #if(i_episode == 2000): #Flush replay memory occasionally
      #replay_memory = set()
env.close()