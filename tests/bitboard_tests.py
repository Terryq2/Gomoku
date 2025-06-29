import pytest

import sys
sys.path.append('C:\\Users\\admin\\Downloads\\Game')
from stones import Stone
from bitboard import BitBoard
from bitboard import InvalidMoveError

def test_place():
    board: BitBoard = BitBoard(15)

    board.place(5, 5, Stone.WHITE)
    assert board.white_rows[5] == 0b000001000000000

    board.place(0, 0, Stone.BLACK)
    assert board.black_rows[0] == 0b100000000000000

    board.place(6, 5, Stone.WHITE)
    assert board.white_rows[5] == 0b000001100000000


def test_place_on_nonempty_cell_raises():
    board: BitBoard = BitBoard(15)
    board.place(6, 5, Stone.WHITE)
    with pytest.raises(InvalidMoveError, match='Position is non empty'):
        board.place(6, 5, Stone.WHITE)

def test_is_empty():
    board: BitBoard = BitBoard(15)

    assert not board.get(5, 5, Stone.WHITE)
    board.place(5, 5, Stone.WHITE)

    assert board.get(5, 5, Stone.WHITE)

    assert not board.get(0, 0, Stone.WHITE)

    assert not board.get(5, 5, Stone.BLACK)

def test_remove():
    board: BitBoard = BitBoard(15)

    assert not board.get(5, 5, Stone.WHITE)
    board.place(5, 5, Stone.WHITE) 
    assert board.get(5, 5, Stone.WHITE)

    board.remove(5, 5, Stone.WHITE)
    assert not board.get(5, 5, Stone.WHITE)

def test_hashing():
    board: BitBoard = BitBoard(15)

    b = board.hash_for_board
    board.place(1, 1, Stone.WHITE)
    board.remove(1, 1, Stone.WHITE)
    a = board.hash_for_board
    assert b == a

    b = board.hash_for_board
    board.place(2, 3, Stone.WHITE)
    board.place(2, 4, Stone.WHITE)
    board.remove(2, 3, Stone.WHITE)
    board.remove(2, 4, Stone.WHITE)

    a = board.hash_for_board

    assert b == a

def test_check_win():
    board: BitBoard = BitBoard(15)

    board.place(0, 0, Stone.WHITE)

    assert not board.check_win(0, 0, Stone.WHITE)

    board.place(1, 0, Stone.WHITE)
    board.place(2, 0, Stone.WHITE)
    board.place(3, 0, Stone.WHITE)
    board.place(4, 0, Stone.WHITE)

    assert board.check_win(4, 0, Stone.WHITE)

def test_check_is_empty():
    board: BitBoard = BitBoard(15)
    assert board.is_empty(0, 0)
    board.place(0, 0, Stone.WHITE)
    assert not board.is_empty(0, 0)

def test_get_col():
    board: BitBoard = BitBoard(15)
    board.place(1, 1, Stone.WHITE)
    assert board.get_column(1, Stone.WHITE) == 0b010000000000000
    board.place(1, 2, Stone.WHITE)
    assert board.get_column(1, Stone.WHITE) == 0b011000000000000

    board.place(2, 3, Stone.WHITE)
    board.place(2, 6, Stone.WHITE)

    assert board.get_column(2, Stone.WHITE) == 0b000100100000000

def test_left_diagonal():
    board: BitBoard = BitBoard(15)
    board.place(3, 8, Stone.WHITE)
    assert board.get_left_diagonal(9, Stone.WHITE) == 0b00010000000
    board.place(0, 6, Stone.WHITE)
    assert board.get_left_diagonal(8, Stone.WHITE) == 0b1000000000
    board.place(3, 9, Stone.WHITE)
    assert board.get_left_diagonal(8, Stone.WHITE) == 0b1001000000

    board.place(12, 1, Stone.WHITE)
    assert board.get_left_diagonal(25, Stone.WHITE) == 0b0100
    board.place(12, 0, Stone.WHITE)
    assert board.get_left_diagonal(26, Stone.WHITE) == 0b100

    board.place(14, 0, Stone.WHITE)
    assert board.get_left_diagonal(28, Stone.WHITE) == 0b1

    board.place(11, 2, Stone.WHITE)
    assert board.get_left_diagonal(23, Stone.WHITE) == 0b001000

def test_right_diagonals():
    board: BitBoard = BitBoard(15)
    board.place(2, 14, Stone.WHITE)
    assert board.get_right_diagonal(16, Stone.WHITE) == 0b1000000000000
    board.place(3, 13, Stone.WHITE)
    assert board.get_right_diagonal(16, Stone.WHITE) == 0b1100000000000


