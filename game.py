##############################################################################
# FILE : game.py
# WRITER : Aviad Dudkewitz
# DESCRIPTION: This program contains the Game class and the battle ship game
# logic.
##############################################################################
from board import *
from ships import *
from random import randint, choice

SHIPS_SIZES = (5,4,3,3,2)
DEFAULT_NUM_OF_COL = 10
DEFAULT_NUM_OF_ROW = 10


class Game:
    """
    represent battle ship game logic.
    """
    GAME_STARTING = -1
    PLAYER1 = 0
    PLAYER2 = 1

    def __init__(self, num_of_row=DEFAULT_NUM_OF_ROW,
                 num_of_col=DEFAULT_NUM_OF_COL):
        """
        :param num_of_row: integer. (has a default value)
        :param num_of_col: integer. (has a default value)
        """
        self.__player1_board = Board(num_of_row, num_of_col)
        self.__player2_board = Board(num_of_row, num_of_col)
        self.__player_turn = Game.GAME_STARTING
        self.__winner = Game.GAME_STARTING

    def set_a_ship(self,player,x,y,length,direction):
        """
        place a ship on the game board.
        :param player: PLAYER1 or PLAYER2
        :param x: integer.
        :param y: integer.
        :param length: integer.
        :param direction: Ship.V_DIR or Ship.H_DIR.
        :return: True if the ship was placed, False otherwise.
        """
        if player == Game.PLAYER1:
            return self.__player1_board.place_a_ship(x,y,length,direction)
        if player == Game.PLAYER2:
            return self.__player2_board.place_a_ship(x, y, length, direction)

    def start_game(self):
        """
        start the game after the ships where placed.
        """
        self.__player_turn = Game.PLAYER1

    def play_a_turn(self, x, y):
        """
        attack the other player board at (x,y).
        :param x: integer.
        :param y: integer.
        :return: a list of coordinates of the tile got hit or the ship that
         have been drown.
        """
        attacked_ship = None
        board_to_attack = None
        if self.__player_turn == Game.PLAYER1:
            board_to_attack = self.__player2_board
        elif self.__player_turn == Game.PLAYER2:
            board_to_attack = self.__player1_board
        if not board_to_attack.can_attack_point(x,y):
            print("You can't attack the same spot twice. select another "
                      "spot.")
        else:
            attacked_ship = board_to_attack.attack(x,y)
            if attacked_ship is not None:
                if attacked_ship.is_alive():
                    return [(x,y)]
                else:
                    if board_to_attack.num_of_ships() == 0:
                        self.__winner = self.__player_turn
                    return attacked_ship.get_coords()
            else:
                self.set_next_turn()
                return []

    def set_next_turn(self):
        """
        move to other player turn.
        """
        if self.__player_turn == Game.PLAYER1:
            self.__player_turn = Game.PLAYER2
        elif self.__player_turn == Game.PLAYER2:
            self.__player_turn = Game.PLAYER1

    def get_winner(self):
        """
        :return: return GAME_STARTING or PLAYER1 or PLAYER2.
        """
        return self.__winner

    def game_over(self):
        """
        :return: True if the game over, False otherwise.
        """
        return self.__winner != Game.GAME_STARTING

    def get_player(self):
        """
        :return: PLAYER1 or PLAYER2
        """
        return self.__player_turn

    def print_board(self, player, reveal):
        """
        meant for debugging.
        :param player: PLAYER1 or PLAYER2
        :param reveal: True to revel unharmed ships, false otherwise.
        :return: a string representing the given board.
        """
        if player == Game.PLAYER1:
            self.__player1_board.print_board(reveal)
        elif player == Game.PLAYER2:
            self.__player2_board.print_board(reveal)

    def get_all_ships_cord(self, player):
        """
        :param player: PLAYER1 or PLAYER2.
        :return: a list of pairs of all ships coordinates.
        """
        if player == Game.PLAYER1:
            return self.__player1_board.get_all_ships_cords()
        elif player == Game.PLAYER2:
            return self.__player2_board.get_all_ships_cords()

"""
This part of the code meant for debugging - to try the game without the GUI.
"""
if __name__ == "__main__":
    new_game = Game()
    for i in range(len(SHIPS_SIZES)):
        success = False
        while not success:
            success = new_game.set_a_ship(1, randint(0, DEFAULT_NUM_OF_COL - 1),
                                          randint(0, DEFAULT_NUM_OF_ROW-1), SHIPS_SIZES[i],
                                          choice([Ship.V_DIR, Ship.H_DIR]))
    possible_targets = [(x, y) for x in range(DEFAULT_NUM_OF_COL)
                        for y in range(DEFAULT_NUM_OF_ROW)]
    for i in range(len(SHIPS_SIZES)):
        success = False
        while not success:
            print("Chose your %i units size ship location:" % SHIPS_SIZES[i])
            success = new_game.set_a_ship(0, int(input("x: ")),
            int(input("y; ")), SHIPS_SIZES[i],
            input("Chose direction. v or h? "))
            if not success:
                print("can't place a ship in there.")
        new_game.print_board(0, True)
    new_game.start_game()
    while(not new_game.game_over()):
        player_turn = new_game.get_player()
        if player_turn == Game.PLAYER1:
            print("Chose location to attack-")
            turn = new_game.play_a_turn(int(input("x: ")), int(input("y: ")))
            if len(turn) == 1:
                print("Bull's-eye!")
            elif len(turn) > 1:
                print("You destroyed an opponent ship!")
            else:
                print("you miss...")
            new_game.print_board(Game.PLAYER2, False)
        elif player_turn == Game.PLAYER2:
            print("Computer turn.")
            location = choice(possible_targets)
            possible_targets.remove(location)
            turn = new_game.play_a_turn(location[0], location[1])
            if len(turn) == 1:
                print("You got hit!")
            elif len(turn) > 1:
                print("You lost a ship!")
            else:
                print("Computer miss...")
            new_game.print_board(0, True)
    if new_game.get_winner() == Game.PLAYER1:
        print("You Won!")
    elif new_game.get_winner() == Game.PLAYER2:
        print("you lose!")



