
from constantes import *
from pecas import *
from move import Move
from casa import Casa
from musica import Musica
import copy
import os


class Tabuleiro:
    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None
        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final

        en_passant_empty = self.squares[final.row][final.col].isempty()

        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        if isinstance(piece, Pawn):
             diff = final.col - initial.col
             if diff != 0 and en_passant_empty:
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Musica(
                        os.path.join('assets/sounds/capture.wav'))
                    sound.play()
            
                else:
                    self.check_promotion(piece, final)

        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.left_rook if (diff < 0) else piece.right_rook
                self.move(rook, rook.moves[-1])

        
            piece.moved = True

            piece.clear_moves()

            self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].piece = Queen(piece.color)

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2

    def set_true_en_passant(self, piece):
        
        if not isinstance(piece, Pawn):
            return

        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False
        
        piece.en_passant = True

    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, testing=True)
        
        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)
                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        
        return False

    def calc_moves(self, piece, row, col, bool=True):
                
        def pawn_moves():
            steps = 1 if piece.moved else 2

            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))
            for possible_move_row in range(start, end, piece.dir):
                if Casa.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].isempty():
                        initial = Casa(row, col)
                        final = Casa(possible_move_row, col)
                        move = Move(initial, final)

                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                        else:
                            piece.add_move(move)
                    else: break
                else: break

            #movimentos diagonais
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]
            for possible_move_col in possible_move_cols:
                if Casa.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        initial = Casa(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Casa(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final)
                        
                        # checar "xeque mate" visiveis
                        if bool:
                            if not self.in_check(piece, move):
                                # adiciona novo movimento
                                piece.add_move(move)
                        else:
                                # adiciona novo movimento
                            piece.add_move(move)

            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5
            if Casa.in_range(col-1) and row == r:
                if self.squares[row][col-1].has_enemy_piece(piece.color):
                    p = self.squares[row][col-1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            initial = Casa(row, col)
                            final = Casa(fr, col-1, p)
                            move = Move(initial, final)
                            
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
            
            if Casa.in_range(col+1) and row == r:
                if self.squares[row][col+1].has_enemy_piece(piece.color):
                    p = self.squares[row][col+1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            initial = Casa(row, col)
                            final = Casa(fr, col+1, p)
                            move = Move(initial, final)
                            
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)


        def knight_moves():
            possible_moves = [
                (row-2, col+1),
                (row-1, col+2),
                (row+1, col+2),
                (row+2, col+1),
                (row+2, col-1),
                (row+1, col-2),
                (row-1, col-2),
                (row-2, col-1),
            ]

            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

                if Casa.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        initial = Casa(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Casa(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final)
                        
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else: break
                        else:
                            piece.add_move(move)

        def straightline_moves(incrs):
            for incr in incrs:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr

                while True:
                    if Casa.in_range(possible_move_row, possible_move_col):
                        initial = Casa(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Casa(possible_move_row, possible_move_col, final_piece)
                        move = Move(initial, final)

                        if self.squares[possible_move_row][possible_move_col].isempty():
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)

                        #inimiga = add movimento + break
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            #checa cheque mates possiveis
                            if bool:
                                if not self.in_check(piece, move):
                                    piece.add_move(move)
                            else:
                                piece.add_move(move)
                            break

                        elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
                            break
                    
                    else: break

                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        def king_moves():
            adjs = [
                (row-1, col+0), # cima
                (row-1, col+1), # cima-direita
                (row+0, col+1), # direita
                (row+1, col+1), # baixo direita
                (row+1, col+0), # baixo
                (row+1, col-1), # baixo esquerda
                (row+0, col-1), # esquerda
                (row-1, col-1), # cima esquerda
            ]

            # movimentos normais
            for possible_move in adjs:
                possible_move_row, possible_move_col = possible_move

                if Casa.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].isempty_or_enemy(piece.color):
                        # checa as casas para novos movimentos
                        initial = Casa(row, col)
                        final = Casa(possible_move_row, possible_move_col) # piece=piece
                        #cria novo movimento
                        move = Move(initial, final)
                        # checa cheque mates potenciais
                        if bool:
                            if not self.in_check(piece, move):
                                piece.add_move(move)
                            else: break
                        else:
                            piece.add_move(move)

            # movimentos de roque
            if not piece.moved:
                # roque rainha
                left_rook = self.squares[row][0].piece
                if isinstance(left_rook, Rook):
                    if not left_rook.moved:
                        for c in range(1, 4):
                            # roque nao e possivel quando ha peças entre elas
                            if self.squares[row][c].has_piece():
                                break

                            if c == 3:
                                # roque para o rei e a torre
                                piece.left_rook = left_rook

                                # movimento torre
                                initial = Casa(row, 0)
                                final = Casa(row, 3)
                                moveR = Move(initial, final)

                                #movimento rei
                                initial = Casa(row, col)
                                final = Casa(row, 2)
                                moveK = Move(initial, final)

                                #checa cheque mate possivel
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(left_rook, moveR):
                                        left_rook.add_move(moveR)
                                        piece.add_move(moveK)
                                else:
                                    left_rook.add_move(moveR)
                                    piece.add_move(moveK)

                # roque rei
                right_rook = self.squares[row][7].piece
                if isinstance(right_rook, Rook):
                    if not right_rook.moved:
                        for c in range(5, 7):
                            # roque nao e possivel quando ha peças entre elas
                            if self.squares[row][c].has_piece():
                                break

                            if c == 6:
                                # roque para direita do rei e torre
                                piece.right_rook = right_rook

                                #movimento torre
                                initial = Casa(row, 7)
                                final = Casa(row, 5)
                                moveR = Move(initial, final)

                                # movimento rei
                                initial = Casa(row, col)
                                final = Casa(row, 6)
                                moveK = Move(initial, final)

                                #checa chque mate possiveis
                                if bool:
                                    if not self.in_check(piece, moveK) and not self.in_check(right_rook, moveR):
                                        right_rook.add_move(moveR)
                                        piece.add_move(moveK)
                                else:
                                    right_rook.add_move(moveR)
                                    piece.add_move(moveK)

        if isinstance(piece, Pawn): 
            pawn_moves()

        elif isinstance(piece, Knight): 
            knight_moves()

        elif isinstance(piece, Bishop): 
            straightline_moves([
                (-1, 1), # cima-direita
                (-1, -1), #cima-esquerda
                (1, 1), # baixo-direita
                (1, -1), #baixo-esquerda
            ])

        elif isinstance(piece, Rook): 
            straightline_moves([
                (-1, 0), # cima
                (0, 1), # direita
                (1, 0), # baixo
                (0, -1), # esquerda
            ])

        elif isinstance(piece, Queen): 
            straightline_moves([
                (-1, 1), # cima-direita
                (-1, -1), # cima-esquerda
                (1, 1), #baixo-direita
                (1, -1), #baixo-esquerda
                (-1, 0), # cima
                (0, 1), # direita
                (1, 0), # baixo
                (0, -1) # esquerda
            ])

        elif isinstance(piece, King): 
            king_moves()

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Casa(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # peoes
        for col in range(COLS):
            self.squares[row_pawn][col] = Casa(row_pawn, col, Pawn(color))

        # cavalos
        self.squares[row_other][1] = Casa(row_other, 1, Knight(color))
        self.squares[row_other][6] = Casa(row_other, 6, Knight(color))

        # bispos
        self.squares[row_other][2] = Casa(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Casa(row_other, 5, Bishop(color))

        # torre
        self.squares[row_other][0] = Casa(row_other, 0, Rook(color))
        self.squares[row_other][7] = Casa(row_other, 7, Rook(color))

        # rainha
        self.squares[row_other][3] = Casa(row_other, 3, Queen(color))

        # rei
        self.squares[row_other][4] = Casa(row_other, 4, King(color))