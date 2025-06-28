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

