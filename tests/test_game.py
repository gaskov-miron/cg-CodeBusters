from unittest import TestCase
from solution import init, step


class TestGame(TestCase):
    def test_game_files(self):
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game1.txt')
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game2.txt')
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game3.txt')
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game4.txt')
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game5.txt')
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game6.txt')

    def test_game_file(self, file_name):
        with open(file_name, 'r') as f:
            lines = ''.join(f.readlines()).split('\n')
            game = init(lines[0] + '\n' + lines[1] + '\n' + lines[2])
            lines = lines[4:]
            blocks = []
            new_block = ''
            for i in lines:
                if i != '' and i != '---':
                    new_block += i + '\n'
                else:
                    blocks.append(new_block[:-1])
                    new_block = ''
            for i in range(0, len(blocks), 3):
                step_out = step(blocks[i], game)
                self.assertEqual(step_out, blocks[i + 1])
