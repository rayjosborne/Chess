#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 14:28:39 2020

@author: raymondosborne
"""

# Chess game

# Board dimensions
# 8x8

import numpy as np

# White player - colour = 1
# Black player - colour = 2
WHITE = 1
BLACK = 2

piece_dt = np.dtype([('piece', np.unicode_, 1), ('colour', np.int)])


# sets up new chess board
def setup_board():
    # create empty board
    board = np.zeros((8, 8), dtype=piece_dt)

    # setup black pieces
    setup_pieces(board, BLACK)

    # setup white pieces
    setup_pieces(board, WHITE)

    # setup empty cells
    for j in range(2, 6):
        for i in range(8):
            board[j, i][0] = ' '

    return board


# sets up pieces for specified colour
def setup_pieces(board, colour):
    if colour == BLACK:
        back_row = 0
        pawn_row = 1
    else:
        back_row = 7
        pawn_row = 6

    # setup pawns and colour for back row
    for i in range(8):
        board[pawn_row, i][0] = 'p'
        board[pawn_row, i][1] = board[back_row, i][1] = colour

    # setup other pieces
    # rooks
    board[back_row, 0][0] = board[back_row, 7][0] = 'r'
    # knights
    board[back_row, 1][0] = board[back_row, 6][0] = 'n'
    # bishops
    board[back_row, 2][0] = board[back_row, 5][0] = 'b'
    # queen
    board[back_row, 3][0] = 'q'
    # king
    board[back_row, 4][0] = 'k'


# prints out the chess board representation in the command line
def display_board(board):
    print("    a   b   c   d   e   f   g   h  ")
    print("   --- --- --- --- --- --- --- --- ")
    for i in range(8):
        row_str = ""
        row_str += str(8-i)+" | "
        for j in range(8):
            if board[i, j][1] == 1:
                row_str += "\033[1;31m"
            else:
                row_str += "\033[0;30m"
            row_str += board[i, j][0] + '\033[0;30m | '
        print(row_str)
        print("   --- --- --- --- --- --- --- --- ")
    print("\n")


# obtains the desired move from the current player (user)
# this loops until a valid move is chosen
def get_move(board, turn_num):
    valid_move = False

    # get move from user, repeat until move is confirmed valid
    while not valid_move:
        move = input("Input start and end coordinates e.g. a2-a3:")
        valid_move = check_move_valid(board, move, turn_num)

    return move


# returns True if the specified move is valid for the current player,
# otherwise returns False
def check_move_valid(board, move, turn_num):
    # check if user wants to quit
    if move == "QUIT":
        return True

    # make sure move is in valid format
    if(len(move) != 5 or move[2] != '-' or not('a' <= move[0] <= 'h') or
       not('a' <= move[3] <= 'h') or not('1' <= move[1] <= '8') or
       not('1' <= move[4] <= '8')):
        return False

    # get start and end coords
    start_row, start_col, end_row, end_col = move_to_coords(move)

    # get expected colour value of current player and their opponent's colour
    if turn_num % 2 == 0:
        exp_colour = BLACK
        opp_colour = WHITE
    else:
        exp_colour = WHITE
        opp_colour = BLACK

    # make sure they are trying to move one of their own pieces
    if board[start_row, start_col][1] != exp_colour:
        return False

    # Make sure not moving piece on top of same coloured piece
    if board[end_row, end_col][1] == exp_colour:
        return False

    # Make sure moving piece in valid fashion
    # first get what piece they're trying to move
    piece_type = board[start_row, start_col][0]

    # Check validity of move for pawn
    if piece_type == 'p':
        # can't move more than two spaces forward or less than 1
        if((abs(start_row-end_row) > 2 or abs(start_row-end_row) < 1)

           # can only move two spaces from its original space
           # and make sure correct colour for such a move
           or (start_row-end_row == 2 and (start_row != 6 or exp_colour != 1))
           or (start_row-end_row == -2 and (start_row != 1 or exp_colour != 2))

           # can't move backwards
           or (start_row-end_row == 1 and exp_colour != 1)
           or (start_row-end_row == -1 and exp_colour != 2)

           # can't move two spaces and diagonal at same time
           or (abs(start_row-end_row) == 2 and start_col != end_col)

           # can't move more than 1 across
           or (abs(start_col - end_col) > 1)

           # can only move diagonal if taking piece
           or(abs(start_col - end_col) == 1 and
              board[end_row, end_col][1] != opp_colour)

           # can only take piece if moving diagonal
           or(abs(start_col - end_col) != 1 and
              board[end_row, end_col][1] == opp_colour)):
            return False

        # Can't move two spaces if there is a piece in between
        if abs(start_row-end_row) == 2:
            row, col = get_cells_between(move)
            # if cell is not empty
            if board[row[0], col[0]][1] != 0:
                return False

    # Check validity of move for rook
    elif piece_type == 'r':
        # can't move diagonally so only one of row or column can change
        if start_row != end_row and start_col != end_col:
            return False
        # make sure it's not trying to pass through other pieces
        if not check_free_path(board, move):
            return False

    # Check validity of move for bishop
    elif piece_type == 'b':
        # must move diagonally so both row or column must change
        if start_row == end_row or start_col == end_col:
            return False
        # must move in perfect diagonal
        if abs(start_col - end_col) != abs(start_row - end_row):
            return False
        # make sure it's not trying to pass through other pieces
        if not check_free_path(board, move):
            return False

    # Check validity of move for queen
    elif piece_type == 'q':
        rows_moved = abs(start_row - end_row)
        cols_moved = abs(start_col - end_col)
        # make sure if it moves in 2 dimensions it moves in a perfect diagonal
        if rows_moved > 0 and cols_moved > 0 and rows_moved != cols_moved:
            return False
        # make sure it's not trying to pass through other pieces
        if not check_free_path(board, move):
            return False

    # Check validity of move for knight
    elif piece_type == 'n':
        # must move to opposite corner of 3x2 rectangle
        rows_moved = abs(start_row - end_row)
        cols_moved = abs(start_col - end_col)
        if not((rows_moved == 2 and cols_moved == 1) or
               (cols_moved == 2 and rows_moved == 1)):
            return False

    # Check validity of move for king
    elif piece_type == 'k':
        # can't move more than 1 square in any direction
        if abs(start_row - end_row) > 1 or abs(start_col - end_col) > 1:
            return False

    # can't end turn in check (or move into check for king)
    if check_for_check(board, move, turn_num):
        return False

    return True


# converts move format to start and end coordinates
def move_to_coords(move):
    start_row = 8 - int(move[1])
    start_col = ord(move[0]) - ord('a')
    end_row = 8 - int(move[4])
    end_col = ord(move[3]) - ord('a')
    return start_row, start_col, end_row, end_col


# converts a row number to move row number
def row_to_move_row(row):
    return str(8-row)


# converts a column number to move column letter
def col_to_move_col(col):
    return chr(col+ord('a'))


# returns the coordinates of the cells between the start and finish location
# for straight line moves including along a perfect diagonal
def get_cells_between(move):
    start_row, start_col, end_row, end_col = move_to_coords(move)

    # define range based on if it is increasing or decreasing
    if start_row > end_row:
        rows_sort = range(start_row-1, end_row, -1)
    else:
        rows_sort = range(start_row+1, end_row)
    if start_col > end_col:
        cols_sort = range(start_col-1, end_col, -1)
    else:
        cols_sort = range(start_col+1, end_col)

    # set rows and columns
    if start_row == end_row:
        cols = cols_sort
        rows = [start_row]*len(cols)
    elif start_col == end_col:
        rows = rows_sort
        cols = [start_col]*len(rows)
    else:
        rows = rows_sort
        cols = cols_sort
    return rows, cols


# checks if there are any pieces along the path of the specified move
# returns False if there are any pieces in the way
def check_free_path(board, move):
    rows, cols = get_cells_between(move)
    for i in range(len(rows)):
        if board[rows[i], cols[i]][1] != 0:
            return False
    return True


# returns True if king would move into check position given the specified
# board and move combination
def check_for_check(board, move, turn_num):
    # first make move to duplicate board
    new_board = dup_board(board)
    if move is not None:
        move_piece(new_board, move)
    if turn_num % 2 == 0:
        opp_colour = WHITE
        king_colour = BLACK
    else:
        opp_colour = BLACK
        king_colour = WHITE

    # get location of target king
    try:
        king_row, king_col = get_loc_of_king(new_board, king_colour)
    except TypeError:
        return True

    # get where all opponent pieces are on the board
    opp_rows, opp_cols = get_coords_opp_pieces(new_board, opp_colour)
    # convert these coordinates to moves
    move_list = []
    for i in range(len(opp_rows)):
        move_list.append(col_to_move_col(opp_cols[i]) +
                         row_to_move_row(opp_rows[i]) + '-' +
                         col_to_move_col(king_col) + row_to_move_row(king_row))
    # check if any of the required moves would be valid
    for test_move in move_list:
        if check_move_valid(new_board, test_move, turn_num+1):
            return True
    return False


# create a duplicate board
def dup_board(board):
    new_board = setup_board()
    for i in range(8):
        for j in range(8):
            for k in range(2):
                new_board[i, j][k] = board[i, j][k]
    return new_board


# enacts the specified move on the board. This function assumes a valid move
def move_piece(board, move):
    start_row, start_col, end_row, end_col = move_to_coords(move)
    board[end_row, end_col][0] = board[start_row, start_col][0]
    board[end_row, end_col][1] = board[start_row, start_col][1]
    board[start_row, start_col][0] = ' '
    board[start_row, start_col][1] = 0


# returns the row and column of the specified player's king
def get_loc_of_king(board, colour):
    for i in range(8):
        for j in range(8):
            if board[i, j][0] == 'k' and board[i, j][1] == colour:
                return i, j


# returns the coordinates of the cells with pieces of the specified
# player colour in them
def get_coords_opp_pieces(board, colour):
    rows = []
    cols = []
    for i in range(8):
        for j in range(8):
            if board[i, j][1] == colour:
                rows.append(i)
                cols.append(j)
    return rows, cols


# checks for checkmate condition and returns True if player is in checkmate
def checkmate(board, turn_counter):
    if turn_counter % 2 == 0:
        opp_colour = WHITE
    else:
        opp_colour = BLACK
    # gets all of the opponent's possible moves and if at least one of them
    # doesn't leave them in check then they aren't in checkmate
    for m in get_all_possible_moves(board, opp_colour, turn_counter+1):
        if not check_for_check(board, m, turn_counter+1):
            return False
    return True


# gets all legal moves for given player
def get_all_possible_moves(board, colour, turn_num):
    move_list = []
    for i in range(8):
        for j in range(8):
            if board[i, j][1] == colour:
                cell = col_to_move_col(j)+row_to_move_row(i)
                piece_moves = get_all_moves_from_cell(board, cell, turn_num)
                for m in piece_moves:
                    move_list.append(m)
    return move_list


# gets all legal move from specified starting position
def get_all_moves_from_cell(board, cell, turn_num):
    move_list = []
    for i in range(8):
        for j in range(8):
            move = cell+'-'+col_to_move_col(j)+row_to_move_row(i)
            if check_move_valid(board, move, turn_num):
                move_list.append(move)
    return move_list


# #############################################################################

# run game
board = setup_board()
turn_counter = 1
forfeit = False
print("To abandon game, type QUIT\n")
print("Legend\n p = Pawn\n r = Rook\n n = Knight\n b = Bishop\n q = Queen\n" +
      " k = King\n")
while True:
    display_board(board)

    if turn_counter % 2 == 0:
        print("Black's turn")
        opp_player = WHITE
    else:
        print("White's (Red) turn")
        opp_player = BLACK

    move = get_move(board, turn_counter)
    if move == "QUIT":
        forfeit = True
        break
    move_piece(board, move)

    # this should not be necessary, but to keep the code working while the
    # checkmate function is being fixed we need this
    # TODO: check if this code is still necessary for the game not to break
    if get_loc_of_king(board, opp_player) is None:
        break

    if checkmate(board, turn_counter):
        break

    turn_counter += 1


display_board(board)

# print out who won
if not forfeit:
    if turn_counter % 2 == 0:
        print("Black Won!")
    else:
        print("White Won!")
else:
    if turn_counter % 2 == 0:
        print("White won by forfeit!")
    else:
        print("Black won by forfeit!")
