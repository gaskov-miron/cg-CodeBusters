from unittest import TestCase
from engine import Entity, Engine


class TestEngine(TestCase):
    def test_engine_file(self):
        blocks = []
        current_block = None
        file_name_new = '/home/miron/work/cg-CodeBusters/tests/game_v2_2.txt'

        block_starters = ['INIT:\n', 'INPUT:\n', 'OUTPUT:\n']
        block_stoppers = ['INIT:\n', 'INPUT:\n', 'OUTPUT:\n', '\n']

        with open(file_name_new, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line in block_stoppers and current_block is not None:
                current_block = None
            if line in block_starters:
                current_block = []
                blocks.append(current_block)
            if current_block is not None and line not in block_stoppers and line not in block_starters:
                current_block.append(line[:-1])

        busters_count, ghosts_count = map(int, blocks[0][:2])
        del blocks[0], blocks[2]
        steps1 = list(zip(blocks[0::4], blocks[1::4]))
        steps2 = list(zip(blocks[2::4], blocks[3::4]))
        busters, ghosts = {}, {}
        for step_ in zip(steps1, steps2):
            for j in range(2):
                for i in step_[j][0]:
                    id_, x, y, type_, state, value = i.split()
                    if type_ == '-1' and int(id_) not in ghosts:
                        ghosts[int(id_)] = Entity(i)
                    if type_ != '-1' and int(id_) not in busters:
                        busters[int(id_)] = Entity(i)
        g = Engine(busters_count, ghosts_count, busters, ghosts)

        for i in range(len(steps1)):
            print(i)
            a = g.get_info(0)
            b = g.get_info(1)
            self.assertEqual('\n'.join(steps1[i][0]), a[:-1])
            self.assertEqual('\n'.join(steps2[i][0]), b[:-1])
            if i < len(steps1) - 1:
                g.do(steps1[i][1], steps2[i][1])

