from flask import Flask, render_template, request, jsonify
import pandas as pd
import random as rnd
import os
from BktModel import BktModel
app = Flask(__name__)


# GLOBAL VARIABLES
WRONG_ANS_FEEDBACK = [
    "Challenges are a sign that you're growing and stretching your mind.",
    "You're showing great perseverance. Keep going!",
    "Every question is a chance to explore and discover.",
    "Your determination is shining through. Keep that positive attitude!",
    "You're building your knowledge step by step. Keep taking those steps!",
    "The more you practice, the more confident you'll become.",
    "Learning involves bumps in the road, and you're navigating them well.",
    "You're a problem solver in the making. Embrace the journey!",
    "Learning is a journey, and you're making progress.",
    "Keep going! Each attempt brings you closer to understanding.",
    "You're getting better with each try. Keep it up!",
    "It's okay not to have all the answers. That's how we learn.",
    "You're working hard, and that's what matters most.",
    "Learning new things can be challenging, but you're doing great.",
    "Every question is an opportunity to learn something new.",
    "Stay curious! Your effort is making a difference.",
    "Don't be discouraged. Challenges make success even sweeter."
]
CORRECT_ANS_FEEDBACK = [
    "Fantastic job! You really know your stuff.",
    "You nailed it! Your hard work is paying off.",
    "Great work! You've got a good grasp on this.",
    "Impressive! You've got a keen understanding.",
    "Well done! You're on top of the material.",
    "Excellent! Your knowledge is shining through.",
    "Bravo! Your effort and focus are paying off.",
    "Outstanding! You're showing real expertise.",
    "Awesome! You've mastered this concept.",
    "Fantastic work! Keep up the great thinking.",
    "You aced it! Your understanding is impressive.",
    "Spot on! You've really grasped the concept.",
    "Excellent job! You're demonstrating real mastery.",
    "Well played! Your knowledge is shining brightly.",
    "Brilliant! You're showing true understanding.",
    "You're on fire! Keep up the excellent work.",
    "Fantastic effort! Your intelligence is shining through.",
    "You're rocking this! Your hard work is paying off.",
    "Superb! You're proving yourself a quick learner.",
    "Terrific! You're making learning look easy."
]
COUNT_MISTAKES = 3  # count how many tries the user have left
USER_NAME = None
TOTAL_SCORE = 0
RANKS = {
            'ADDITION_RANK': 0,
            'SUBTRACTION_RANK': 0,
            'MULTIPLICATION_RANK': 0,
            'DIVISION_RANK': 0
        }
ADDITION_BKT = BktModel("addition_game")
SUBTRACTION_BKT = BktModel("subtraction_game")
MULTIPLICATION_BKT = BktModel("multiplication_game")
DIVISION_BKT = BktModel("division_game")


def update_df(df, user_id, equation, correct_answer, user_answer, difficulty_level, response):
    df.loc[len(df.index)] = [user_id, equation, correct_answer, user_answer, difficulty_level, response]
    return df


def save_df_to_csv(df, filename):
    df.to_csv(filename, index=False)


def load_df_from_csv(filename, fields):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=fields)


def update_csv_file(current_username, new_data, name_or_password):
    global USER_NAME
    df_users = pd.read_csv("UsersDB.csv")

    msg = ''
    # updating the column value/data
    for i in range(len(df_users["user_name"])):
        if df_users["user_name"][i] == current_username:
            if name_or_password == 'n':
                if new_data in df_users["user_name"].values and new_data != current_username:
                    msg = "The user name " + new_data + " is already taken,\n please choose a different one"
                else:
                    df_users.loc[i, 'user_name'] = new_data
                    USER_NAME = new_data
                    print(f'update_csv_file {USER_NAME}')
            elif name_or_password == 'p':
                df_users.loc[i, 'password'] = new_data

    # writing into the file
    save_df_to_csv(df_users, filename="UsersDB.csv")
    return msg


def create_df_questions():
    return pd.DataFrame(columns=['user_id', 'equation', 'correct_answer',
                                 'user_answer', 'difficulty_level', 'response'])


def get_next_level(curr_level):
    levels = ["easy", "easy-medium", "medium", "medium-hard", "hard", "advanced"]
    flag = False
    next_level = None

    if curr_level == "advanced":
        return "advanced"

    for level in levels:
        if flag:
            next_level = level
            flag = False
        if curr_level == level:
            flag = True
    return next_level


def get_prev_level(curr_level):
    levels = ["easy", "easy-medium", "medium", "medium-hard", "hard", "advanced"]
    flag = False
    prev_level = None

    if curr_level == "easy":
        return "easy"

    for level in reversed(levels):
        if flag:
            prev_level = level
            flag = False
        if curr_level == level:
            flag = True
    return prev_level


def img_path_eq(equation):
    images_path = []
    for char in equation:
        if char != " ":
            images_path.append(f'static/images/{char}.jpg')
    return images_path


def filter_df(df, difficulty_level):
    df_filtered = df[df['difficulty_level'] == difficulty_level]
    return df_filtered


def get_equation(df, next_difficulty_level):
    df_filtered = filter_df(df, next_difficulty_level)
    random_row = df_filtered.sample(n=1)

    variable1 = random_row['variable1'].iloc[0]
    operator = random_row['operator'].iloc[0]
    variable2 = random_row['variable2'].iloc[0]
    equation = f'{variable1} {operator} {variable2} ='
    return equation


def update_and_predict_next(bkt_model, current_difficulty_level, response):
    # Update the BKT model with the current data and predict the mastery probability at the next difficulty level

    next_mastery_prob = bkt_model.update_and_predict_next_level(current_difficulty_level, response)
    current_mastery_prob = bkt_model.levels[current_difficulty_level]

    # Print the current difficulty level and its mastery probability
    print(f'current_difficulty_level: {current_difficulty_level} , mastery_prob: {current_mastery_prob}')

    # Print the next difficulty level and its predicted mastery probability
    print(f'predicted: next_difficulty_level: {get_next_level(current_difficulty_level)} , mastery_prob: {next_mastery_prob}')

    if current_mastery_prob > 0.65 and next_mastery_prob > 0.5:
        # If mastery probability at the next level is high, move to the next difficulty level
        next_difficulty_level = get_next_level(current_difficulty_level)
        print(f"going up a level {next_difficulty_level}")
    elif current_mastery_prob < 0.05:
        # If mastery probability at the next level is low, move to the previous difficulty level
        next_difficulty_level = get_prev_level(current_difficulty_level)
        print(f"going down a level {next_difficulty_level}")
    else:
        next_difficulty_level = current_difficulty_level

    return next_difficulty_level


@app.route("/user_signup", methods=['POST'])
def user_signup():
    global USER_NAME, ADDITION_BKT, SUBTRACTION_BKT, MULTIPLICATION_BKT, DIVISION_BKT

    signup_successful = False
    user_name = str(request.form['user_name'])
    user_password = str(request.form['user_password'])
    password_confirmation = str(request.form['password_confirmation'])

    df_users = pd.read_csv("UsersDB.csv")
    if user_password == password_confirmation:
        if user_name in df_users["user_name"].values:
            msg = "The user name " + user_name + " is already taken, please choose a different one"
        else:
            msg = "Signup completed successfully ! Welcome " + user_name + " !"
            signup_successful = True
    else:
        msg = "Password and confirmed password do not match,\n" \
              "please check them and try again (:"

    if signup_successful:  # create new user entry and set new models
        USER_NAME = user_name
        addition_bkt_levels = ADDITION_BKT.get_levels()
        subtraction_bkt_levels = SUBTRACTION_BKT.get_levels()
        multiplication_bkt_levels = MULTIPLICATION_BKT.get_levels()
        division_bkt_levels = DIVISION_BKT.get_levels()

        df_users.loc[len(df_users.index)] = [USER_NAME, user_password, "easy", "easy", "easy", "easy",
                                             0, 0, 0, 0, 0, addition_bkt_levels, subtraction_bkt_levels,
                                             multiplication_bkt_levels, division_bkt_levels]
        save_df_to_csv(df_users, filename="UsersDB.csv")

    return jsonify(flag=signup_successful, message=msg)


@app.route("/user_login", methods=['POST'])
def user_login():
    global USER_NAME, TOTAL_SCORE, RANKS, ADDITION_BKT, SUBTRACTION_BKT, MULTIPLICATION_BKT, DIVISION_BKT

    login_successful = True
    user_name = str(request.form['username'])
    user_password = str(request.form['userpassword'])
    df_users = pd.read_csv("UsersDB.csv")
    user_entry = df_users[df_users['user_name'] == user_name]
    stored_password = ""
    msg = ''

    if not user_entry.empty:
        stored_password = user_entry.iloc[0]['password']
    if user_entry.empty or user_password != str(stored_password):
        msg = "User name or password are incorrect\n" \
              "if you are already registered please try again,\n" \
              "if not please register"
        login_successful = False

    if login_successful:  # load saved data
        USER_NAME = user_name
        user_row = df_users.loc[df_users['user_name'] == USER_NAME].iloc[0]

        addition_bkt_levels = eval(str(user_row['addition_bkt']))
        subtraction_bkt_levels = eval(str(user_row['subtraction_bkt']))
        multiplication_bkt_levels = eval(str(user_row['multiplication_bkt']))
        division_bkt_levels = eval(str(user_row['division_bkt']))

        ADDITION_BKT = ADDITION_BKT.set_levels(addition_bkt_levels)
        SUBTRACTION_BKT = SUBTRACTION_BKT.set_levels(subtraction_bkt_levels)
        MULTIPLICATION_BKT = MULTIPLICATION_BKT.set_levels(multiplication_bkt_levels)
        DIVISION_BKT = DIVISION_BKT.set_levels(division_bkt_levels)

        TOTAL_SCORE = user_row['total_score']

        RANKS = {
            'ADDITION_RANK': user_row['addition_score'],
            'SUBTRACTION_RANK': user_row['subtraction_score'],
            'MULTIPLICATION_RANK': user_row['multiplication_score'],
            'DIVISION_RANK': user_row['division_score']
        }

    return jsonify(message=msg, flag=login_successful)


@app.route("/password_hint", methods=['POST'])
def password_hint():
    username = str(request.form['username'])
    df_users = pd.read_csv("UsersDB.csv")
    user_entry = df_users[df_users['user_name'] == username]
    if not user_entry.empty:
        stored_password = str(user_entry.iloc[0]['password'])
        hint = stored_password[0]
        msg = "Password Hint: Your password begins with " + hint
    else:
        msg = "User name " + username + " does not exist,\n please check it and try again"
    return jsonify(msg=msg)


@app.route("/")
def login_page():
    return render_template('login_page.html')


@app.route("/home_page")
def home_page():
    global RANKS
    # Define recommendations based on the minimum rank
    recommendations = {
        'ADDITION_RANK': "Focus on addition problems",
        'SUBTRACTION_RANK': "Work on subtraction problems",
        'MULTIPLICATION_RANK': "Practice multiplication problems",
        'DIVISION_RANK': "Improve your division skills"
    }

    min_rank = min(RANKS.values())

    recommendation = []
    # Find all ranks that are equal to the minimum rank
    for math_rank in recommendations:
        if RANKS[math_rank] == min_rank:
            recommendation.append(recommendations[math_rank])

    return render_template('home_page.html', data=recommendation)


@app.route("/update_user_info", methods=['POST'])
def update_user_info():
    current_user_name = request.json.get('current_user_name')
    new_data = request.json.get('new_data')
    name_or_password = request.json.get('name_or_password')

    msg = update_csv_file(current_user_name, new_data, name_or_password)
    return jsonify(message=msg)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/profile")
def profile():
    global USER_NAME
    df_user = pd.read_csv("UsersDB.csv")
    # user_name = username
    user_entry = df_user[df_user['user_name'] == USER_NAME]
    user_password = ''
    user_addition_score = ''
    user_subtraction_score = ''
    user_multiplication_score = ''
    user_division_score = ''
    user_total_score = ''

    if not user_entry.empty:
        user_password = user_entry.iloc[0]['password']
        user_addition_score = user_entry.iloc[0]['addition_score']
        user_subtraction_score = user_entry.iloc[0]['subtraction_score']
        user_multiplication_score = user_entry.iloc[0]['multiplication_score']
        user_division_score = user_entry.iloc[0]['division_score']
        user_total_score = user_entry.iloc[0]['total_score']
    return render_template('profile.html', user_name=USER_NAME, password=user_password,
                           addition_score=user_addition_score, subtraction_score=user_subtraction_score,
                           multiplication_score=user_multiplication_score, division_score=user_division_score,
                           total_score=user_total_score)


@app.route("/score_board")
def score_board():
    df_users = pd.read_csv("UsersDB.csv")
    df = df_users[['user_name', 'total_score']]

    df_sorted = df.sort_values(by='total_score', ascending=False)
    top_10_users = df_sorted.head(10)

    return render_template('score_board.html', users=top_10_users)


@app.route("/save_parameters", methods=['POST'])
def save_parameters():
    global USER_NAME, RANKS, TOTAL_SCORE, ADDITION_BKT, SUBTRACTION_BKT, MULTIPLICATION_BKT, DIVISION_BKT

    df_users = pd.read_csv("UsersDB.csv")

    page_type = str(request.form['type'])
    current_difficulty_level = str(request.form['current_level'])

    user_row = df_users.loc[df_users['user_name'] == USER_NAME].iloc[0]

    user_row['total_score'] = TOTAL_SCORE

    if page_type == 'addition_game':
        user_row['addition_level'] = current_difficulty_level
        user_row['addition_score'] = RANKS['ADDITION_RANK']
        user_row['addition_bkt'] = ADDITION_BKT.get_levels()
    elif page_type == 'subtraction_game':
        user_row['subtraction_level'] = current_difficulty_level
        user_row['subtraction_score'] = RANKS['SUBTRACTION_RANK']
        user_row['subtraction_bkt'] = SUBTRACTION_BKT.get_levels()
    elif page_type == 'multiplication_game':
        user_row['multiplication_level'] = current_difficulty_level
        user_row['multiplication_score'] = RANKS['MULTIPLICATION_RANK']
        user_row['multiplication_bkt'] = MULTIPLICATION_BKT.get_levels()
    else:
        user_row['division_level'] = current_difficulty_level
        user_row['division_score'] = RANKS['DIVISION_RANK']
        user_row['division_bkt'] = DIVISION_BKT.get_levels()

    df_users[df_users['user_name'] == USER_NAME] = user_row
    save_df_to_csv(df_users, filename='UsersDB.csv')

    return "Parameters saved successfully!"


@app.route("/check_answer", methods=['POST'])
def check_answer():
    global COUNT_MISTAKES, TOTAL_SCORE, RANKS, USER_NAME,\
        ADDITION_BKT, SUBTRACTION_BKT, MULTIPLICATION_BKT, DIVISION_BKT

    page_type = str(request.form['page_type'])
    print(page_type)

    if page_type == 'addition_game':
        df_equations = df_addition
        df_questions = df_addition_questions
        bkt_model = ADDITION_BKT
        print(ADDITION_BKT.levels)

    elif page_type == 'subtraction_game':
        df_equations = df_subtraction
        df_questions = df_subtraction_questions
        bkt_model = SUBTRACTION_BKT
    elif page_type == 'multiplication_game':
        df_equations = df_multiplication
        df_questions = df_multiplication_questions
        bkt_model = MULTIPLICATION_BKT
    else:
        df_equations = df_division
        df_questions = df_division_questions
        bkt_model = DIVISION_BKT

    operator_functions = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '|': lambda x, y: x / y
    }

    current_difficulty_level = str(request.form['difficulty_level'])
    user_answer = int(request.form['user_answer'])
    equation_str = str(request.form['equation'])

    equation_lst = equation_str.split(" ")
    var1 = int(equation_lst[0])
    operator = str(equation_lst[1])
    var2 = int(equation_lst[2])

    correct_answer = operator_functions[operator](var1, var2)

    if user_answer == correct_answer:
        response = 1  # correct answer
        TOTAL_SCORE += total_scores[operator][current_difficulty_level]

        if page_type == 'addition_game':
            RANKS['ADDITION_RANK'] += recommendation_ranks[current_difficulty_level]
        elif page_type == 'subtraction_game':
            RANKS['SUBTRACTION_RANK'] += recommendation_ranks[current_difficulty_level]
        elif page_type == 'multiplication_game':
            RANKS['MULTIPLICATION_RANK'] += recommendation_ranks[current_difficulty_level]
        else:
            RANKS['DIVISION_RANK'] += recommendation_ranks[current_difficulty_level]

        msg = 'Correct! ' + rnd.choice(CORRECT_ANS_FEEDBACK)
        next_difficulty_level = update_and_predict_next(bkt_model, current_difficulty_level, response)
    else:
        response = 0  # incorrect answer
        TOTAL_SCORE -= total_scores[operator][current_difficulty_level]
        COUNT_MISTAKES -= 1

        if COUNT_MISTAKES == 0:
            msg = "You are out of tries, Lets try to solve a new equation"
            next_difficulty_level = update_and_predict_next(bkt_model, current_difficulty_level, response)
        else:
            msg = rnd.choice(WRONG_ANS_FEEDBACK) + f'.\nTry Again you got {COUNT_MISTAKES} tries left for this equation'
            next_difficulty_level = current_difficulty_level

    df_questions = update_df(df_questions, USER_NAME, equation_str, correct_answer,
                                        user_answer, current_difficulty_level, response)

    exist = True
    new_equation = get_equation(df_equations, next_difficulty_level)

    while exist:
        if new_equation in df_questions[df_questions['user_id'] == USER_NAME]['equation'].tail(5).values:
            new_equation = get_equation(df_equations, next_difficulty_level)
        else:
            exist = False

    if response == 1 or COUNT_MISTAKES == 0:
        COUNT_MISTAKES = 3  # count how many tries user have left

        # flag = True: display the new equation
        return jsonify(message=msg, data=new_equation, flag=True, difficulty_level=next_difficulty_level)
    else:
        # flag = False: display again the current equation
        return jsonify(message=msg, data=" ", flag=False, difficulty_level=current_difficulty_level)


@app.route("/addition_game")
def addition_game():
    global USER_NAME
    df_users = pd.read_csv("UsersDB.csv")

    user_row = df_users[df_users['user_name'] == USER_NAME].iloc[0]
    current_difficulty_level = user_row['addition_level']

    df_filtered = filter_df(df_addition, current_difficulty_level)
    random_row = df_filtered.sample(n=1)
    variable1 = random_row['variable1'].iloc[0]
    variable2 = random_row['variable2'].iloc[0]
    difficulty_level = random_row['difficulty_level'].iloc[0]
    equation = f'{variable1} + {variable2} ='

    images_path = img_path_eq(equation)
    return render_template('addition_game.html', data=equation, images_path=images_path,
                           difficulty_level=difficulty_level)


@app.route("/subtraction_game")
def subtraction_game():
    global USER_NAME

    df_users = pd.read_csv("UsersDB.csv")

    user_row = df_users.loc[df_users['user_name'] == USER_NAME].iloc[0]
    current_difficulty_level = user_row['subtraction_level']

    df_filtered = filter_df(df_subtraction, current_difficulty_level)
    random_row = df_filtered.sample(n=1)
    variable1 = random_row['variable1'].iloc[0]
    variable2 = random_row['variable2'].iloc[0]
    difficulty_level = random_row['difficulty_level'].iloc[0]
    equation = f'{variable1} - {variable2} ='

    images_path = img_path_eq(equation)
    return render_template('subtraction_game.html', data=equation, images_path=images_path,
                           difficulty_level=difficulty_level)


@app.route("/multiplication_game")
def multiplication_game():
    global USER_NAME

    df_users = pd.read_csv("UsersDB.csv")

    user_row = df_users.loc[df_users['user_name'] == USER_NAME].iloc[0]
    current_difficulty_level = user_row['multiplication_level']

    df_filtered = filter_df(df_multiplication, current_difficulty_level)
    random_row = df_filtered.sample(n=1)
    variable1 = random_row['variable1'].iloc[0]
    variable2 = random_row['variable2'].iloc[0]
    difficulty_level = random_row['difficulty_level'].iloc[0]
    equation = f'{variable1} * {variable2} ='

    images_path = img_path_eq(equation)
    return render_template('multiplication_game.html', data=equation, images_path=images_path,
                           difficulty_level=difficulty_level)


@app.route("/divide_game")
def divide_game():
    global USER_NAME

    df_users = pd.read_csv("UsersDB.csv")

    user_row = df_users.loc[df_users['user_name'] == USER_NAME].iloc[0]
    current_difficulty_level = user_row['division_level']

    df_filtered = filter_df(df_division, current_difficulty_level)
    random_row = df_filtered.sample(n=1)
    variable1 = random_row['variable1'].iloc[0]
    variable2 = random_row['variable2'].iloc[0]
    difficulty_level = random_row['difficulty_level'].iloc[0]
    equation = f'{variable1} | {variable2} ='

    images_path = img_path_eq(equation)
    return render_template('divide_game.html', data=equation, images_path=images_path,
                           difficulty_level=difficulty_level)


if __name__ == '__main__':
    # Load Equations CSV
    df_addition = pd.read_csv('/Users/danielvaanunu/PycharmProjects/MathGame/Addition.csv')
    df_subtraction = pd.read_csv('/Users/danielvaanunu/PycharmProjects/MathGame/Subtraction.csv')
    df_multiplication = pd.read_csv('/Users/danielvaanunu/PycharmProjects/MathGame/Multiplication.csv')
    df_division = pd.read_csv('/Users/danielvaanunu/PycharmProjects/MathGame/Division.csv')

    # Created only once for saving users data
    users = load_df_from_csv('UsersDB.csv', fields=['user_name', 'password', 'addition_level', 'subtraction_level',
                                                       'multiplication_level', 'division_level', 'addition_score',
                                                       'subtraction_score', 'multiplication_score', 'division_score',
                                                       'total_score', 'addition_bkt', 'subtraction_bkt',
                                                       'multiplication_bkt', 'division_bkt'])
    save_df_to_csv(users, filename='UsersDB.csv')

    # Created every session
    df_addition_questions = create_df_questions()
    df_subtraction_questions = create_df_questions()
    df_multiplication_questions = create_df_questions()
    df_division_questions = create_df_questions()

    total_scores = {
        "+": {
            "easy": 10,
            "easy-medium": 15,
            "medium": 20,
            "medium-hard": 25,
            "hard": 30,
            "advanced": 35
        },
        "-": {
            "easy": 20,
            "easy-medium": 25,
            "medium": 30,
            "medium-hard": 35,
            "hard": 40,
            "advanced": 45
        },
        "*": {
            "easy": 30,
            "easy-medium": 35,
            "medium": 40,
            "medium-hard": 45,
            "hard": 50,
            "advanced": 55
        },
        "|": {
            "easy": 40,
            "easy-medium": 45,
            "medium": 50,
            "medium-hard": 55,
            "hard": 60,
            "advanced": 65
        }
    }

    recommendation_ranks = {
        "easy": 1,
        "easy-medium": 2,
        "medium": 3,
        "medium-hard": 4,
        "hard": 5,
        "advanced": 6
    }

    app.run()

