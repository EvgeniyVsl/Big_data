"""
Given a Tic-Tac-Toe 3x3 board (can be unfinished).
Write a function that checks if the are some winners.
If there is "x" winner, function should return "x wins!"
If there is "o" winner, function should return "o wins!"
If there is a draw, function should return "draw!"
If board is unfinished, function should return "unfinished!"

Example:
    [[-, -, o],
     [-, x, o],
     [x, o, x]]
    Return value should be "unfinished"

    [[-, -, o],
     [-, o, o],
     [x, x, x]]

     Return value should be "x wins!"

"""
from typing import List

board = [
     ['x', '-', '-'],
     ['o', 'o', 'o'],
     ['o', 'o', 'x']]

def tic_tac_toe_checker(board: List[List]) -> str:
    
    result = None

    # строка
    for line in board:
        if line[0] == line[1] == line[2] and line[0] != '-':
            result = f'{line[0]} wins!'
            
    # столбец
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != '-':
            result = f'{board[0][i]} wins!'

    # диагональ
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != '-':
        result = f'{board[0][0]} wins!'
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != '-':
        result = f'{board[0][2]} wins!'

    # результат
    if not result:
        result = 'unfinished'

    return result

print(tic_tac_toe_checker(board))