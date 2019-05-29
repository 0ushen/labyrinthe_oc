import unittest
from labyrinthe.playstyle import *


class TestPlayStyle(unittest.TestCase):

    def setUp(self):
        self.testMap = [
            'OOOOOOO\n',
            'O   X O\n',
            'O     U\n',
            'O  O OO\n',
            'OOOOOOO\n']
        self.rX = 4
        self.rY = 1

    def test_current_position(self):
        coord = current_position(self.testMap)
        true_coord = Coord((self.rX, self.rY))
        msg = 'coord incorrect :  expected value is {} and we found {}'
        msg = msg.format(true_coord, coord)
        self.assertEqual(true_coord, coord, msg)

    def test_change_obj(self):
        pos = Coord((3, 1))
        msg = 'Incorrect Object at pos {} : expected {} , got {}'
        change_obj(self.testMap, pos, 'O')
        self.assertEqual(self.testMap[1][3], 'O',
                         msg.format(pos, 'O', self.testMap[1][3]))
        change_obj(self.testMap, pos, ' ')
        self.assertEqual(self.testMap[1][3], ' ',
                         msg.format(pos, ' ', self.testMap[1][3]))

    def test_detect_collision(self):
        pos1 = Coord((1, 3))
        pos2 = Coord((4, 3))
        b = detect_collision(self.testMap, pos1, pos2)
        self.assertTrue(b, '')

    def test_play_turn(self):
        # testing bad input
        _, is_valid, msg = play_turn(self.testMap, '*8')
        self.assertFalse(is_valid, msg)
        _, is_valid, msg = play_turn(self.testMap, 's$')
        self.assertFalse(is_valid, msg)
        # testing map limit checking
        _, is_valid, msg = play_turn(self.testMap, 'e5')
        self.assertFalse(is_valid, msg)
        # testing wall collision
        _, is_valid, msg = play_turn(self.testMap, 'e2')
        self.assertFalse(is_valid, msg)
        _, is_valid, msg = play_turn(self.testMap, 'w4')
        self.assertFalse(is_valid, msg)
        # testing a regular move
        _, is_valid, msg = play_turn(self.testMap, 's1')
        self.assertTrue(is_valid, msg)
        # testing when robot finds the escape
        end, is_valid, msg = play_turn(self.testMap, 'e2')
        self.assertTrue(is_valid, msg)
        self.assertTrue(end, msg)
