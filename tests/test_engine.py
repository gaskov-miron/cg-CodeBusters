from unittest import TestCase
from engine import init, step


class TestEngine(TestCase):
    def test_engine_file(self):
        file_name = '/home/miron/work/cg-CodeBusters/tests/game_v2_3.txt'
        with open(file_name, 'r') as f:
            lis = ''.join(f.readlines()).split('\n')
            file_s = ''
            for i in lis:
                file_s += i+'\n'
            z = 0
            dic = {}
            bus1 = {}
            bus2 = {}
            for i in lis:
                inf = i.split()
                if len(inf) == 6:
                    if inf[3] == '-1' and inf[0] not in dic:
                        dic[inf[0]] = inf[1]+' '+inf[2]+' '+inf[4]+' '+inf[5]
            for i in range(int(lis[4])):
                if str(i) not in dic:
                    dic[str(i)] = 'None None None None'
            i1 = 0
            i2 = 0
            while len(bus1) != int(lis[3]):
                inf = lis[i1].split()
                if len(inf) == 6:
                    if inf[3] == lis[5] and inf[0] not in bus1:
                        bus1[inf[0]] = inf[1]+' '+inf[2]+' '+inf[4]+' '+inf[5]
                i1 += 1
            while len(bus2) != int(lis[3]):
                inf = lis[i2].split()
                if len(inf) == 6:
                    if inf[3] == str(int(lis[5] == '0')) and inf[0] not in bus2:
                        bus2[inf[0]] = inf[1]+' '+inf[2]+' '+inf[4]+' '+inf[5]
                i2 += 1
        i1, i2 = init(bus1, bus2, dic)
        self.assertEqual(i1, file_s.split('---')[1][1:])
        self.assertEqual(i2, file_s.split('---')[3][1:])
        for i in range(3, len(file_s.split('\n\n'))-8, 8):
            o1, o2 = step(file_s.split('\n\n')[i], file_s.split('\n\n')[i+4], i//3)
            self.assertEqual(o1[:-1], file_s.split('\n\n')[i+6].split('---')[0][:-1])
            self.assertEqual(o2[:-1], file_s.split('\n\n')[i+10].split('---')[0][:-1])
