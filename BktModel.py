import numpy as np
from NeuralNetwork import NeuralNetwork
from sklearn.preprocessing import OneHotEncoder
import torch
import torch.nn as nn
import torch.optim as optim


class BktModel:
    def __init__(self, type):
        """
        Initialize the Bayesian Knowledge Tracing model.

        Parameters:
        - type (str): type of game
        - learn_rate (float): The learning rate for the model.
        - forget_rate (float): The forgetting rate for the model.
        - p_guess (float): Probability of guessing.
        - p_slip (float): Probability of slipping.
        - p_init (float): Initial probability of mastery.
        """

        self.type = type

        # Initialize difficulty levels
        self.levels = {
            'easy': None,
            'easy-medium': None,
            'medium': None,
            'medium-hard': None,
            'hard': None,
            'advanced': None
        }
        self.learn_rate = 0.4  # typically range from 0.1 to 0.5
        self.p_guess = 0.2  # typically range from 0.1 to 0.3
        self.p_slip = 0.1  # typically range from 0.05 to 0.2

        self.forget_rate = 0.05

        self.p_init = 0.2  # for the game

        # Initialize prior knowledge for each skill
        for level in self.levels:
            self.levels[level] = self.p_init

        # Initialize the neural network model
        self.model = NeuralNetwork()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.BCELoss()  # Binary Cross Entropy Loss

    def get_levels(self):
        return self.levels

    def set_levels(self, new_levels):
        for level, mastery_prob in new_levels.items():
            self.levels[level] = mastery_prob
        return self

    def preprocess_data(self, level, response):
        """
        Preprocess data for training the neural network.

        Parameters:
        - level (str): The difficulty level.
        - response (int): Binary response (0: incorrect, 1: correct).
        """
        encoded_level = np.array([self.encode_level(level)], dtype=np.float32)
        X = torch.tensor(encoded_level, dtype=torch.float32)
        y = torch.tensor([response], dtype=torch.float32).view(-1, 1)
        return X, y

    def encode_level(self, level):
        """
        Encode difficulty level using one-hot encoding.

        Parameters:
        - level (str): The difficulty level.

        Returns:
        - array: One-hot encoded representation of the difficulty level.
        """
        encoder = OneHotEncoder(categories=[list(self.levels.keys())], sparse_output=False)
        encoded_level = encoder.fit_transform([[level]])
        return encoded_level.flatten()

    def update_and_predict_next_level(self, current_level, response):
        """
        Update the model with the current interaction data and predict
         the probability of mastery at the next difficulty level.

        Parameters:
        - level (str): The difficulty level.
        - response (int): Binary response (0: incorrect, 1: correct).

        Returns:
        - float: The predicted probability of mastery at the next difficulty level.
        """
        self.update(current_level, response)

        X, y = self.preprocess_data(current_level, response)
        self.model.train()
        self.optimizer.zero_grad()
        output = self.model(X)
        loss = self.criterion(output, y)
        loss.backward()
        self.optimizer.step()

        next_level = self.get_next_level(current_level)  # Get the next difficulty level
        encoded_next_level = np.array(self.encode_level(next_level))  # Encode the next difficulty level

        # predict the probability of mastery at the next difficulty level
        with torch.no_grad():
            self.model.eval()
            return self.model(torch.tensor(encoded_next_level, dtype=torch.float32)).item()

    def update(self, level, response):
        """
        Update the learner's knowledge state based on the response at a given difficulty level.

        Parameters:
        - level (str): The difficulty level.
        - response (int): Binary response (0: incorrect, 1: correct).
        """
        # Check if the given level exists
        if level not in self.levels:
            raise ValueError("Invalid difficulty level")

        # Calculate probability of mastery based on response, taking into account guessing and slipping
        if response == 1:
            """ p_correct = the probability of the learner knowing and not slipping +
                           the probability of the learner not knowing and guessing correctly"""
            p_correct = self.levels[level] * (1 - self.p_slip) + (1 - self.levels[level]) * self.p_guess

            # Update the knowledge state due to learning
            self.levels[level] += self.learn_rate * (p_correct - self.levels[level])

        else:
            """ p_incorrect = the probability of the learner knowing and slipping + 
                              the probability of the learner not knowing and guessing incorrectly"""
            p_incorrect = self.levels[level] * self.p_slip + (1 - self.levels[level]) * (1 - self.p_guess)

            # Calculate the additional decay due to answering incorrectly
            incorrect_decay = (1 - self.levels[level]) * p_incorrect

            # Calculate the decay due to forgetting
            forgetting_decay = self.forget_rate * self.levels[level]

            # Update the knowledge state by subtracting both decays
            self.levels[level] -= (incorrect_decay + forgetting_decay)

        # Ensure probabilities stay within bounds
        self.levels[level] = max(min(self.levels[level], 1.0), 0.0)

    def get_next_level(self, curr_level):
        """
        Get the next difficulty level.

        Parameters:
        - level (str): The current difficulty level.

        Returns:
        - str: The next difficulty level.
        """

        flag = False
        next_level = None

        if curr_level == "advanced":
            return "advanced"

        for level in self.levels.keys():
            if flag:
                next_level = level
                flag = False
            if curr_level == level:
                flag = True
        return next_level