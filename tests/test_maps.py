import unittest
from labyrinthe import maps


class MapTest(unittest.TestCase):
    """Test case utilisé pour tester les fonctionnalités du module 'maps'."""

    def setUp(self):
        self.objects = {'wall': 'O',
                        'door': '.',
                        'robot': 'X',
                        'escape': 'U',
                        'empty': ' '}

    def test_load_map(self):
        maps.show_maps()
        test_map = maps.load_map(0)
        self.assertIsInstance(test_map, list)
        for y, row in enumerate(test_map):
            self.assertIsInstance(row, str)
            for x, letter in enumerate(row):
                if x == len(row) - 1:
                    self.assertEqual(letter, '\n', f'Letter {x} of row {y}')
                elif y == 0 or x == 0 or x == len(row) - 2:
                    self.assertTrue(letter == self.objects['wall'] or
                                    letter == self.objects['escape'],
                                    f'Letter {x} of row {y}')
                else:
                    self.assertIn(letter, self.objects.values(),
                                  f'Letter {x} of row {y}')

    def test_save_map(self):
        pass

    def test_delete_finished_map(self):
        pass
