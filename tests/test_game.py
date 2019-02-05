from unittest import TestCase
from solution import init, step


class TestGame(TestCase):
    def test_game_files(self):
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game1.txt')
        #self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game2.txt')
        #self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game3.txt')
        #self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game4.txt')
        #self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game5.txt')
        #self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game6.txt')

    def test_game_file(self, file_name):
        block_starters = ['INIT:\n', 'INPUT:\n', 'OUTPUT:\n']
        block_stoppers = ['INIT:\n', 'INPUT:\n', 'OUTPUT:\n', '\n']
        current_block = None
        blocks = []
        with open(file_name, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line in block_stoppers and current_block is not None:
                current_block = None
            if line in block_starters:
                current_block = []
                blocks.append(current_block)
            if current_block is not None and line not in block_stoppers and line not in block_starters:
                current_block.append(line[:-1])
        game = init('\n'.join(blocks[0]))
        del blocks[0]
        for i in range(0, len(blocks), 2):
            game.update('\n'.join(blocks[i]))
            print(game.step, game.ghosts[1].is_filled())
            step_out = step(game)
            self.assertEqual(step_out, '\n'.join(blocks[i + 1]))
