from unittest import TestCase
from solution import init, step


class TestGame(TestCase):
    def test_game_files(self):
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game1.txt')
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game2.txt')
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game3.txt')
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game4.txt')
        self.test_game_file('/home/miron/work/cg-CodeBusters/tests/game5.txt')

    def test_game_file(self, file_name):
        with open(file_name, 'r') as f:
            lis = ''.join(f.readlines()).split('\n')
            init(lis[0] + '\n' + lis[1] + '\n' + lis[2])
            lis = lis[4:]
            d = []
            t = ''
            for i in lis:
                if i != '' and i != '---':
                    t += i + '\n'
                else:
                    d.append(t[:-1])
                    t = ''
            for i in range(0, len(d), 3):
                step_out = step(d[i])
                self.assertEqual(step_out, d[i + 1])
