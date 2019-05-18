##############################################################################
# FILE : ships.py
# WRITER : Aviad Dudkewitz
# DESCRIPTION: This program contains the Ship class.
##############################################################################
class Ship:
    """
    represent a ship on board.
    """
    V_DIR = "v"
    H_DIR = "h"

    def __init__(self, col, row, length, direction):
        """
        :param col: integer
        :param row: integer
        :param length: integer
        :param direction: V_DIR or H_DIR
        """
        self.__length = length
        self.__col = col
        self.__row = row
        self.__direction = direction
        self.__life = self.__length
        self.__alive = True

    def hit(self):
        """
        loss 1 life. die if life is zero.
        """
        self.__life -=1
        if self.__life == 0:
            self.__alive = False

    def is_alive(self):
        """
        :return: if ship still alive or not.
        """
        return self.__alive

    def get_coords(self):
        """
        :return: all the ship coordinates in a list of pairs.
        """
        result = []
        x = self.__col
        y = self.__row
        for i in range(self.__length):
            result.append((x,y))
            if self.__direction == Ship.H_DIR:
                x += 1
            elif self.__direction == Ship.V_DIR:
                y += 1
        return result

    def __len__(self):
        """
        :return: length
        """
        return self.__length

