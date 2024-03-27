import random as rnd
import pandas as pd

REP = 1000
DIFFICULTY_LEVELS = ["easy", "easy-medium", "medium", "medium-hard", "hard", "advanced"]


def update_df(df, var1, operator, var2, result, difficulty_level):
    df.loc[len(df.index)] = [var1, operator, var2, result, difficulty_level]


# + equations generator
def addition_csv(fields):
    df_addition = pd.DataFrame(columns=fields)

    for level in DIFFICULTY_LEVELS:
        for idx in range(REP):
            if level == "easy":  # v1 + v2 <= 10
                var1 = rnd.randint(0, 9)
                var2 = rnd.randint(0, 10-var1)
            elif level == "easy-medium":  # v1 + v2 > 10, v1,v2 < 10
                var1 = rnd.randint(2, 9)
                var2 = rnd.randint(10 - var1 + 1, 9)
            elif level == "medium":  # v1 + v2 <= 100, v1 < 10, 10<=v2<=99
                var1 = rnd.randint(0, 9)
                var2 = rnd.randint(10, 100-var1)
            elif level == "medium-hard":  # v1 + v2 <= 100, 10<=v2,v1<=99
                var1 = rnd.randint(10, 90)
                var2 = rnd.randint(10, 100 - var1)
            elif level == "hard":  # v1 + v2 > 100, 10<=v2,v1<=99
                var1 = rnd.randint(10, 99)
                var2 = rnd.randint(100 - var1 + 1, 99)
            else: # v1 + v2 < 1000, 10<=v1<=99, 100<=v2<=990
                var1 = rnd.randint(10, 99)
                var2 = rnd.randint(100, 1000 - var1)

            res = var1 + var2
            update_df(df_addition, var1, '+', var2, res, level)
    # remove duplicates
    df_addition = df_addition.drop_duplicates()
    # export to csv file
    df_addition.to_csv("Addition.csv", index=False)


# - equations generator
def subtraction_csv(fields):
    df_subtraction = pd.DataFrame(columns=fields)

    for level in DIFFICULTY_LEVELS:
        for idx in range(REP):
            if level == "easy":  # v1 - v2 <= 10
                var1 = rnd.randint(0, 10)
                var2 = rnd.randint(0, var1)
            elif level == "easy-medium":  # v1 - v2 > 10 & the result doesnt change the 10th digit, 11<v1<=99 , 1 <= v2 <=9
                var1 = rnd.randint(11, 99)
                if var1 % 10 == 0:
                    var2 = rnd.randint(1, 9)
                else:
                    var2 = rnd.randint(1, var1 % 10)
            elif level == "medium":  # v1 - v2 <= 100,  10<=v2<=99, 10<=v2<=99
                var1 = rnd.randint(10, 99)
                var2 = rnd.randint(10, var1)
            elif level == "medium-hard":  # v1 - v2 > 100 & the result doesnt change the 100th digit, 110<=v1<=999 , 10<=v2<=99
                var1 = rnd.randint(110, 999)
                var2 = rnd.randint(0, var1 % 100)
            elif level == "hard":  # 100<=v2<=999, 10<=v2<=99
                var1 = rnd.randint(100, 999)
                var2 = rnd.randint(10, 99)
            else:  # 100<=v1,v2<=990
                var1 = rnd.randint(100, 999)
                var2 = rnd.randint(100, var1)

            res = var1 - var2
            update_df(df_subtraction, var1, '-', var2, res, level)
    # remove duplicates
    df_subtraction = df_subtraction.drop_duplicates()
    # export to csv file
    df_subtraction.to_csv("Subtraction.csv", index=False)


# * equations generator
def multiplication_csv(fields):
    df_multiplication = pd.DataFrame(columns=fields)

    for level in DIFFICULTY_LEVELS:
        for idx in range(REP):
            if level == "easy":  # v1* v2 < 100, v1 = 10,0,1
                # Generate a random choice from the options
                options = [10, 0, 1]
                var1 = rnd.choice(options)
                var2 = rnd.randint(0, 99)
            elif level == "easy-medium":  # 2<=v1<=5 ,2<=v2<=9
                var1 = rnd.randint(2, 5)
                var2 = rnd.randint(2, 9)
            elif level == "medium":  # 6<=v1,v2<=9
                var1 = rnd.randint(6, 9)
                var2 = rnd.randint(6, 9)
            elif level == "medium-hard":  # v1*v2<=100, 2<=v1<=5 ,11<=v2<=20
                var1 = rnd.randint(2, 5)
                var2 = rnd.randint(11, 20)
            elif level == "hard":  # 6<=v1<=9, 10<=v2<=99
                var1 = rnd.randint(2, 9)
                if var1 < 6:
                    var2 = rnd.randint(21, 99)
                else:
                    var2 = rnd.randint(11, 99)
            else:  # 10<=v1,v2<=99
                var1 = rnd.randint(11, 99)
                var2 = rnd.randint(11, 99)

            res = var1 * var2
            update_df(df_multiplication, var1, '*', var2, res, level)
    # remove duplicates
    df_multiplication = df_multiplication.drop_duplicates()
    # export to csv file
    df_multiplication.to_csv("Multiplication.csv", index=False)


# / equations generator
def divide_csv(fields):
    df_divide = pd.DataFrame(columns=fields)

    for level in DIFFICULTY_LEVELS:
        for idx in range(REP):
            if level == "easy":  # v1/v2, v2 = 1,v1
                var1 = rnd.randint(0, 99)
                # Generate a random choice from the options
                if var1 != 0:
                    options = [1, var1]
                    var2 = rnd.choice(options)
                else:
                    var2 = rnd.randint(1, 99)
            elif level == "easy-medium":  # v1/v2 ,1<=v1<=50, v2 = 2,5,10
                # Generate a random choice from the options
                options = [2, 5, 10]
                var2 = rnd.choice(options)
                var1 = rnd.randrange(var2, 50, var2)
            elif level == "medium":  # v1/v2 ,1<=v1<=50, v2 = 3,4,6,7,8,9
                # Generate a random choice from the options
                options = [3, 4, 6, 7, 8, 9]
                var2 = rnd.choice(options)
                var1 = rnd.randrange(var2 * 2, 50, var2)
            elif level == "medium-hard":  # v1/v2 ,50<=v1<=100, v2 = 2,5,10
                options = [2, 5, 10]
                var2 = rnd.choice(options)
                var1 = rnd.randrange(50, 100, var2)
            elif level == "hard":  # 50<=v1<=100, v2 = 3,4,6,7,8,9
                options = [3, 4, 6, 7, 8, 9]
                var2 = rnd.choice(options)
                var1 = rnd.randrange(((50//var2) * var2) + var2, 100, var2)
            else:  # 2<=v1<=9 , 100<=v2<=999
                var2 = rnd.randint(2, 9)
                var1 = rnd.randrange(((100//var2) * var2) + var2, 999, var2)

            res = var1 / var2
            update_df(df_divide, var1, '|', var2, res, level)
    # remove duplicates
    df_divide = df_divide.drop_duplicates()
    # export to csv file
    df_divide.to_csv("Division.csv", index=False)


def main():
    fields = ['variable1', 'operator', 'variable2', 'result', 'difficulty_level']
    # addition_csv(fields)
    # subtraction_csv(fields)
    # multiplication_csv(fields)
    divide_csv(fields)


if __name__ == "__main__":
    main()
