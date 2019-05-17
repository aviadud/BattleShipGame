##############################################################################
# FILE : Battleship.py
# WRITER : Aviad Dudkewitz
# DESCRIPTION: This program run the battleship game. This game uses an Internet
# connection to allow two players to play against each other. Also it allow to
# play against a random choosing opponent.
# To run the game, the given arguments for the program should be as follows:
# <player_type> <port> <ip>
# player_type - "human" or "random"
# port - self explanatory.
# ip - server should omit that, and client should input the server ip.
# ##############################################################################
import sys
import socket
from communicator import Communicator
from game import Game
from board import Board
from random import randint, choice
import tkinter as tk

ARG_ERROR = "Illegal program arguments."
MIN_ARG_NUM = 3
MAX_ARG_NUM = 4
LEGAL_PORT = range(65535)
LEGAL_PLAYER = ("human", "random")
SELF = 0
OPPONENT = 1
WAIT_PERIOD = 100       # The wait period between two read attempts.
LONGER_WAIT_PERIOD = 1500
NUM_OF_COL = 10
NUM_OF_ROW = 10
SHIPS_SIZES = (5,4,3,3,2)
WINDOW_W = 768
WINDOW_H = 416
MSG_DISPLAY_CORD = (384 ,32)
TILE_W = 32
TILE_H = 32
ENEMY_BOARD_X = 32
ENEMY_BOARD_Y = 64
SELF_BOARD_X = 416
SELF_BOARD_Y = 64
TILE_BG = "#%02x%02x%02x" % (0,156,222)
BACKGROUND_IMG = "background.png"
TILE_IMG = "tile.png"
TARGET_IMG = "target.png"
SHIP_FRONT_V = ("bsvf.png", "bsvfd.png")
SHIP_MIDDLE_V = ("bsvm.png", "bsvmd.png")
SHIP_BOTTOM_V = ("bsvb.png", "bsvbd.png")
SHIP_FRONT_H = ("bshf.png", "bshfd.png")
SHIP_MIDDLE_H = ("bshm.png", "bshmd.png")
SHIP_BOTTOM_H = ("bshb.png", "bshbd.png")
#moods:
CONNECTING = 0
SETTING_UP = 1
WAITING_FOR_OPPONENT = 2
PLAYER_TURN = 3
OPPONENT_TURN = 4
GAME_OVER = 5
# massages
CONNECTING_MSG = "Waiting for connection..."
STARTING_GAME_MSG = "Connection successfully established. Starting a new game..."
SETTING_UP_MSG = "Place your ships"
WRONG_SHIP_SETTING_MSG = "you can't place a ship in there."
WAITING_FOR_OPPONENT_MSG = "Waiting for opponent to set up his ships."
PLAYER_TURN_MSG = "It's your turn."
OPPONENT_TURN_MSG = "It's opponent turn."
MISS_MSG = "You miss..."
SUCCESS_MSG = "Bull's-eye!"
HIT_MSG = "You got hit!"
LOSE_A_SHIP_MSG = "You lost a ship..."
DROWNING_OPPONENT_SHIP_MSG = "You destroyed an opponent ship!"
WIN_MSG = "You win!"
LOSE_MSG = "You lose..."


class GUI:

    def __init__(self, root, game, port, ip=None):
        self._root = root
        self.__game = game
        self.__state = CONNECTING
        self.__enemy_tiles = []
        self.__self_tiles = []
        self.__ship_dir = Board.H_DIR
        self.__communicator = Communicator(self._root, port, ip)
        self.__communicator.connect()
        self.__random_player = (player_type == LEGAL_PLAYER[1])
        self.__random_possible_targets = [(x, y) for x in range(NUM_OF_COL)
                        for y in range(NUM_OF_ROW)]
        self.__communicator.bind_action_to_message(self.__handle_message)
        self.__place_widgets()
        self.__check_connection()

    def __place_widgets(self):
        # background
        self.__background_img = tk.PhotoImage(file=BACKGROUND_IMG)
        self.__tile_img = tk.PhotoImage(file=TILE_IMG)
        self._canvas = tk.Canvas(self._root, width=WINDOW_W,
                                 height=WINDOW_H)
        self._canvas.create_image((0, 0), anchor=tk.NW,
                                  image=self.__background_img)
        self._canvas.pack(side=tk.TOP)
        # massage display
        self.__display_msg = self._canvas.create_text(MSG_DISPLAY_CORD,
                            font=("Jockey One", 20), fill="white"
                                                      ,text=CONNECTING_MSG)
        # enemy board
        for x in range(NUM_OF_COL):
            for y in range(NUM_OF_ROW):
                self.__enemy_tiles.append(EnemyTile(x,y,self._root,self))
        # player board
        for x in range(NUM_OF_COL):
            for y in range(NUM_OF_ROW):
                self.__self_tiles.append(SelfTile(x,y,self._root,self))

    def __fix_display_msg(self):
        if self.__state == CONNECTING:
            self._canvas.itemconfigure(self.__display_msg, text=CONNECTING_MSG)
        elif self.__state == SETTING_UP:
            self._canvas.itemconfigure(self.__display_msg, text=SETTING_UP_MSG)
        elif self.__state == WAITING_FOR_OPPONENT:
            self._canvas.itemconfigure(self.__display_msg,
                                       text=WAITING_FOR_OPPONENT_MSG)
        elif self.__state == PLAYER_TURN:
            self._canvas.itemconfigure(self.__display_msg,
                                       text=PLAYER_TURN_MSG)
        elif self.__state == OPPONENT_TURN:
            self._canvas.itemconfigure(self.__display_msg,
                                       text=OPPONENT_TURN_MSG)
        elif self.__state == GAME_OVER:
            if self.__game.get_winner() == player_num:
                self._canvas.itemconfigure(self.__display_msg, text=WIN_MSG)
            else:
                self._canvas.itemconfigure(self.__display_msg, text=LOSE_MSG)

    def __check_connection(self):
        if self.__communicator.is_connected():
            self.__state = SETTING_UP
            self.__enemy_placed_ships=0
            self.__ship_index=0
            self._canvas.itemconfigure(self.__display_msg,
                                       text=STARTING_GAME_MSG)
            self._root.after(LONGER_WAIT_PERIOD, self.__fix_display_msg)
            self._root.bind("<ButtonPress-3>", self.__switch_v_h)
            self._root.bind("<space>", self.__switch_v_h)
            if self.__random_player:
                self._root.after(WAIT_PERIOD, self.__random_place_ship)
        else:
            self._root.after(WAIT_PERIOD, self.__check_connection)

    def __random_place_ship(self):
        self.__ship_dir = choice([Board.V_DIR, Board.H_DIR])
        self.player_place_a_ship(randint(0, NUM_OF_ROW - 1),
                                 randint(0, NUM_OF_COL - 1))

    def player_place_a_ship(self, row, col):
        if self.__game.set_a_ship(player_num, col, row,
                            SHIPS_SIZES[self.__ship_index], self.__ship_dir):
            self.__communicator.send_message("%d,%d,%d," %
                    (col,row,SHIPS_SIZES[self.__ship_index]) + self.__ship_dir)
            self.__create_a_ship(SELF, col, row,
                                SHIPS_SIZES[self.__ship_index],self.__ship_dir)
            self.__ship_index += 1
            if self.__ship_index == len(SHIPS_SIZES):
                self.__state = WAITING_FOR_OPPONENT
                self.__fix_display_msg()
                self.__start_game()

            elif self.__random_player:
                self._root.after(LONGER_WAIT_PERIOD, self.__random_place_ship)
        else:
            self._canvas.itemconfigure(self.__display_msg,
                                       text=WRONG_SHIP_SETTING_MSG)
            self._root.after(LONGER_WAIT_PERIOD, self.__fix_display_msg)
            if self.__random_player:
                self._root.after(LONGER_WAIT_PERIOD, self.__random_place_ship)

    def __create_a_ship(self, player, col, row, length, direction):
        for i in range(length):
            current_tile = self.get_tile(row, col, player)
            if i==0:
                if direction == Board.H_DIR:
                    current_tile.add_ship(SHIP_FRONT_H)
                elif direction == Board.V_DIR:
                    current_tile.add_ship(SHIP_FRONT_V)
            elif i==length-1:
                if direction == Board.H_DIR:
                    current_tile.add_ship(SHIP_BOTTOM_H)
                elif direction  == Board.V_DIR:
                    current_tile.add_ship(SHIP_BOTTOM_V)
            else:
                if direction == Board.H_DIR:
                    current_tile.add_ship(SHIP_MIDDLE_H)
                elif direction  == Board.V_DIR:
                    current_tile.add_ship(SHIP_MIDDLE_V)
            if player == SELF:
                current_tile.show_ship()
            if direction == Board.H_DIR:
                col += 1
            if direction == Board.V_DIR:
                row += 1

    def __switch_v_h(self, event):
        if self.__ship_dir == Board.H_DIR:
            self.__ship_dir = Board.V_DIR
        elif self.__ship_dir == Board.V_DIR:
            self.__ship_dir = Board.H_DIR

    def __start_game(self):
        if self.__enemy_placed_ships == len(SHIPS_SIZES) and\
                self.__ship_index == len(SHIPS_SIZES):
            self.__game.start_game()
            if player_num == Game.PLAYER1:
                self.__state = PLAYER_TURN
                if self.__random_player:
                    self._root.after(LONGER_WAIT_PERIOD,
                                     self.__play_a_random_turn)
            elif player_num == Game.PLAYER2:
                self.__state = OPPONENT_TURN
            self.__fix_display_msg()

    def __play_a_random_turn(self):
            location = choice(self.__random_possible_targets)
            self.__random_possible_targets.remove(location)
            self.play_a_turn(location[0], location[1])

    def play_a_turn(self, col, row):
        if self.__state == PLAYER_TURN:
            coords_got_hit = self.__game.play_a_turn(col, row)
            if len(coords_got_hit) == 0:
                self.get_tile(row,col,OPPONENT).got_a_hit()
                self._canvas.itemconfigure(self.__display_msg,
                                           text=MISS_MSG)
                self.__state = OPPONENT_TURN
                self._root.after(LONGER_WAIT_PERIOD, self.__fix_display_msg)
            else:
                self.get_tile(row, col, OPPONENT).got_a_hit()
                if len(coords_got_hit) == 1:
                    self._canvas.itemconfigure(self.__display_msg,
                                               text=SUCCESS_MSG)
                else:
                    for c in coords_got_hit:
                        self.get_tile(c[1],c[0],OPPONENT).show_ship()
                    self._canvas.itemconfigure(self.__display_msg,
                                               text=DROWNING_OPPONENT_SHIP_MSG)
                if self.__random_player:
                    self._root.after(LONGER_WAIT_PERIOD,
                                     self.__play_a_random_turn)
            self.__communicator.send_message("%d,%d" % (col, row))
            if self.__game.game_over():
                self.__state = GAME_OVER
                self.__game_over()

    def state(self):
        return self.__state

    def get_tile(self, row, col, player):
        if 0<= col < NUM_OF_COL and 0<= row < NUM_OF_ROW:
            if player:
                return self.__enemy_tiles[row + col*NUM_OF_ROW]
            else:
                return self.__self_tiles[row + col*NUM_OF_ROW]

    def __handle_message(self, text=None):
        if text:
            if (self.__state == SETTING_UP or
                    self.__state == WAITING_FOR_OPPONENT) and\
                    self.__enemy_placed_ships < len(SHIPS_SIZES):
                opponent_move = text.split(",")
                if player_num == game.PLAYER1:
                    opponent = game.PLAYER2
                else:
                    opponent = game.PLAYER1
                self.__game.set_a_ship(opponent, int(opponent_move[0]),
                        int(opponent_move[1]), int(opponent_move[2]),
                                           opponent_move[3])
                self.__create_a_ship(OPPONENT, int(opponent_move[0]),
                        int(opponent_move[1]), int(opponent_move[2]),
                                           opponent_move[3])
                self.__enemy_placed_ships += 1
                if self.__enemy_placed_ships == len(SHIPS_SIZES):
                    self.__start_game()
            elif self.__state == OPPONENT_TURN:
                opponent_move = text.split(",")
                coords_got_hit = self.__game.play_a_turn(int(opponent_move[0]),
                                                      int(opponent_move[1]))
                self.get_tile(int(opponent_move[1]), int(opponent_move[0]),
                              SELF).got_a_hit()
                if len(coords_got_hit) == 1:
                    self._canvas.itemconfigure(self.__display_msg,
                                               text=HIT_MSG)
                elif len(coords_got_hit) > 1:
                    self._canvas.itemconfigure(self.__display_msg,
                                               text=LOSE_A_SHIP_MSG)
                else:
                    self.__state = PLAYER_TURN
                    self._canvas.itemconfigure(self.__display_msg,
                                               text=PLAYER_TURN_MSG)
                    if self.__random_player:
                        self.__play_a_random_turn()
                if self.__game.game_over():
                    self.__state = GAME_OVER
                    self.__game_over()

    def __game_over(self):
        self.__fix_display_msg()
        if self.__game.get_winner() != player_num:
            if player_num == game.PLAYER1:
                opponent = game.PLAYER2
            else:
                opponent = game.PLAYER1
            list_of_cords = self.__game.get_all_ships_cord(opponent)
            for i in list_of_cords:
                self.get_tile(i[1],i[0],True).show_ship()


class Tile:

    def __init__(self, col, row, root, gui):
        self._col = col
        self._row = row
        self._root = root
        self._gui = gui
        self._tile_img = tk.PhotoImage(file=TILE_IMG)
        self._ship_img = None
        self._ship_img_files = None
        self._canvas = tk.Canvas(self._root, width=TILE_W, height=TILE_H,
                                 highlightthickness=0, bg=TILE_BG)
        self._canvas.create_image((0,0), anchor=tk.NW, image=self._tile_img)
        self._ship = self._canvas.create_image((0,0) ,anchor=tk.NW,
                                               state=tk.HIDDEN)
        if player_type==LEGAL_PLAYER[0]:
            self._canvas.bind("<Enter>", self.enter_tile)
            self._canvas.bind("<Leave>", self.leave_tile)
            self._canvas.bind("<ButtonPress-1>", self.tile_chosen)
        self._is_occupied = False
        self._got_hit = False

    def enter_tile(self, event):
        pass

    def leave_tile(self, event):
        pass

    def tile_chosen(self, event):
        pass

    def add_ship(self, images):
        self._is_occupied = True
        self._ship_img_files = images
        self._ship_img = tk.PhotoImage(file=self._ship_img_files[0])
        self._canvas.configure(bg=TILE_BG)
        self._canvas.itemconfigure(self._ship, image=self._ship_img)

    def show_ship(self):
        self._canvas.itemconfigure(self._ship, state=tk.NORMAL)

    def got_a_hit(self):
        self._got_hit = True
        if self._is_occupied:
            self._ship_img = tk.PhotoImage(file=self._ship_img_files[1])
            self._canvas.itemconfigure(self._ship, image=self._ship_img)
            self._canvas.configure(bg="red")
        else:
            self._canvas.configure(bg="white")


class EnemyTile(Tile):

    def __init__(self, col, row, root, gui):
        super().__init__(col, row, root, gui)
        self._canvas.place(relx=0, anchor=tk.NW, x= col*TILE_W + ENEMY_BOARD_X,
                                                y= row*TILE_H + ENEMY_BOARD_Y)
        self._target_img = tk.PhotoImage(file=TARGET_IMG)
        self._highlight = self._canvas.create_image((0, 0), anchor=tk.NW,
                                    image=self._target_img, state=tk.HIDDEN)

    def enter_tile(self, event):
        if self._gui.state() == PLAYER_TURN and not self._got_hit:
            self._canvas.itemconfigure(self._highlight, state=tk.NORMAL)

    def leave_tile(self, event):
        if self._gui.state() == PLAYER_TURN and not self._got_hit:
            self._canvas.itemconfigure(self._highlight, state=tk.HIDDEN)

    def tile_chosen(self, event):
        if self._gui.state() == PLAYER_TURN and not self._got_hit:
            self._canvas.itemconfigure(self._highlight, state=tk.HIDDEN)
            self._gui.play_a_turn(self._col, self._row)


class SelfTile(Tile):
    def __init__(self, col, row, root, gui):
        super().__init__(col, row, root, gui)
        self._canvas.place(relx=0, anchor=tk.NW,
                           x=col * TILE_W + SELF_BOARD_X,
                           y=row * TILE_H + SELF_BOARD_Y)

    def enter_tile(self, event):
        if self._gui.state() == SETTING_UP and not self._is_occupied:
            self._canvas.configure(bg="white")

    def leave_tile(self, event):
        if self._gui.state() == SETTING_UP and not self._is_occupied:
            self._canvas.configure(bg=TILE_BG)

    def tile_chosen(self, event):
        if self._gui.state() == SETTING_UP and not self._is_occupied:
            self._gui.player_place_a_ship(self._row, self._col)


def valid_input(arg):
    """
    Receive the input and check if valid, if not print appropriate
    message and return False, if yes returns True.
    :param arg: the arg given to the program in the cmd:
    :return: True or False
    """
    if MIN_ARG_NUM <= len(arg) <= MAX_ARG_NUM and arg[1] in LEGAL_PLAYER \
            and arg[2].isdigit() and int(arg[2]) in LEGAL_PORT:
        return True
    else:
        print(ARG_ERROR)
        return False


if __name__ == '__main__':
    if valid_input(sys.argv):
        root = tk.Tk()
        player_type = sys.argv[1]
        port = int(sys.argv[2])
        game = Game(NUM_OF_ROW, NUM_OF_COL)
        print(socket.gethostbyname(socket.gethostname())) # prints the ip
        # address to aid connecting to the server.
        if len(sys.argv) == MAX_ARG_NUM:
            ip = sys.argv[3]
            player_num = game.PLAYER2
            root.title("Client")
            GUI(root, game, port, ip)
        else:
            player_num = game.PLAYER1
            root.title("Server")
            GUI(root, game, port)
        root.mainloop()