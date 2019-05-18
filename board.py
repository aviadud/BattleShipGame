##############################################################################
# FILE : board.py
# WRITER : Aviad Dudkewitz
# DESCRIPTION: This program contains the Board class and BoardTile class.
##############################################################################
from ships import *


class Board:
    """
    represent battle ship board.
    """
    V_DIR = Ship.V_DIR
    H_DIR = Ship.H_DIR

    def __init__(self, num_of_row, num_of_col):
        """
        allow board to be not equilateral rectangle.
        :param num_of_row: integer.
        :param num_of_col: integer.
        """
        self.num_of_col = num_of_col
        self.num_of_row = num_of_row
        self.__board = []
        self.__ships = []
        self.__num_of_alive_ships = 0
        for x in range(num_of_col):
            self.__board.append([])
            for y in range(num_of_row):
                self.__board[x].append(BoardTile(x, y))


    def place_a_ship(self,x,y,length,direction):
        """
        place a ship in valid coordinate on the board.
        :param x: integer.
        :param y: integer.
        :param length: integer.
        :param direction: Ship.V_DIR or Ship.H_DIR
        :return: True if the ship was placed, False otherwise.
        """
        if direction == Board.V_DIR:
            y2 = y+(length-1)
            x2 = x
        if direction == Board.H_DIR:
            x2 = x+(length-1)
            y2 =y
        if self.__check_if_tiles_free(x, y, x2, y2):
            new_ship = Ship(x, y, length, direction)
            for coord in new_ship.get_coords():
                self.__board[coord[0]][coord[1]].add_ship(new_ship)
            self.__ships.append(new_ship)
            self.__num_of_alive_ships +=1
            return True
        else:
            return False

    def attack(self,x,y):
        """
        attack a spot
        :param x: integer.
        :param y: integer.
        :return: return the ship that got attacked, or None if miss.
        """
        if self.__board[x][y].got_a_hit():
            print("You can't hit the same place twice.")
        else:
            return_ship = self.__board[x][y].set_a_hit()
            if return_ship is not None and not return_ship.is_alive():
                self.__num_of_alive_ships -= 1
            return return_ship

    def can_attack_point(self, x, y):
        """
        :param x: integer.
        :param y: integer.
        :return: true if the tile at the given coordinate got attacked,
        false otherwise or for invalid coordinate.
        """
        return not self.__board[x][y].got_a_hit() and 0<=x<=self.num_of_col\
                                        and 0<=y<=self.num_of_row

    def num_of_ships(self):
        """
        :return: number if alive ships.
        """
        return self.__num_of_alive_ships

    def __check_if_tiles_free(self, x1, y1, x2, y2):
        """
        check if the given tiles from (x1,y1) to (x2,y2) are free from other
         ships and valid.
        :param x1: integer.
        :param y1: integer.
        :param x2: integer.
        :param y2: integer.
        :return: true or false
        """
        if x1 <0 or x2> self.num_of_col-1 or y1<0 or y2 > self.num_of_row-1:
            return False
        for x in range(x1,x2+1):
            for y in range(y1, y2 +1):
                if self.__board[x][y].is_occupied():
                    return False
        return True

    def print_board(self, reveal_ships):
        """
        This method meant for debugging.
        :param reveal_ships: true or false to show the ships on board (to hide
        enemy ships).
        :return: a string representing the board.
        """
        return_string = ""
        for y in range(self.num_of_row):
            return_string += "-"*(self.num_of_col * 2+1) + "\n|"
            for x in range(self.num_of_col):
                return_string += self.__board[x][y].tile_symble(reveal_ships)\
                                 + "|"
            return_string += "\n"
        return_string += "-" * (self.num_of_col * 2 + 1) + "\n"
        print(return_string)

    def get_all_ships_cords(self):
        """
        :return: a list of pairs of all ships coordinates.
        """
        result = []
        for ship in self.__ships:
            result += ship.get_coords()
        return result


class BoardTile:
    """
    represent a tile in the game board.
    """

    GOT_HIT_OC_SYB = "X"
    GOT_HIT_EMPTY_SYB = "#"
    SHIP_SYB = "0"
    NONE_SYB = " "

    def __init__(self, x, y,):
        """
        :param x: integer.
        :param y: integer.
        """
        self.__x = x
        self.__y = y
        self.__got_hit = False
        self.__is_occupied = False
        self.__ship = None

    def add_ship(self, ship):
        """
        make tile occupied and get a reference to the ship.
        :param ship: the ship that occupied the tile.
        """
        self.__ship = ship
        self.__is_occupied = True

    def set_a_hit(self):
        """
        :return: if the if occupied - return the ship. else - return None.
        """
        self.__got_hit = True
        if self.__is_occupied:
            self.__ship.hit()
            return self.__ship
        return None

    def got_a_hit(self):
        """
        :return: if the tile was attacked.
        """
        return self.__got_hit

    def is_occupied(self):
        """
        :return: if a ship was placed in the tile.
        """
        return self.__is_occupied

    def tile_symble(self, reveal_ship):
        """
        :param reveal_ship: true to show the ship, false to show the ship
        only if got hit.
        :return: a character representing the tile.
        """
        if self.__got_hit:
            if self.__is_occupied:
                return BoardTile.GOT_HIT_OC_SYB
            else:
                return BoardTile.GOT_HIT_EMPTY_SYB
        else:
            if self.__is_occupied and reveal_ship:
                return BoardTile.SHIP_SYB
            else:
                return BoardTile.NONE_SYB