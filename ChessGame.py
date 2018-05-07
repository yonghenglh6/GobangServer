import numpy as np
import time
import cPickle as pickle
import ChessBoard

class ChessGame(object):

    def __init__(self):
        self.board_size = 15
        pass

    def init_board(self):
        self.chess_board = ChessBoard(self.board_size)
        
        
    def join_game(self,uid):
        pass