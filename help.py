import pandas as pd

# df_addition = pd.read_csv('/Users/danielvaanunu/PycharmProjects/MathGame/Addition.csv')
# df_filtered = df_addition[df_addition['difficulty_level'] == 'easy']
# random_row = df_filtered.sample(n=1)
#
# variable1 = random_row['variable1'].iloc[0]
# operator = random_row['operator'].iloc[0]
# variable2 = random_row['variable2'].iloc[0]
# result = random_row['result'].iloc[0]
# difficulty_level = random_row['difficulty_level'].iloc[0]
#
# print(variable1, operator, variable2)

# def reset_params(self):
#     self.learn_rate = 0.3
#     self.forget_rate = 0.1
#     self.p_guess = 0.2
#     self.p_slip = 0.1
#     self.p_transit = 0.2
#     self.p_init = 0.2
#
#     for level in self.levels:
#         if self.levels[level] is None:
#             self.levels[level] = self.p_init


import pyttsx3


def text_to_speech(text):
    """
    Function to convert text to speech
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def text_to_speech(text):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("Error occurred during text-to-speech conversion:", e)

# Call the function with some text
text_to_speech("Hello, this is a test message.")



