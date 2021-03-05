# TODO __select method by_idx

import os
import random
import bisect
from itertools import accumulate
from typing import Tuple, List, Union
from Source import Source
ParsedCommand = List[Union[int, Tuple[int, int]]]

class Controller():
    def __init__(self, sourcefile: str) -> None:
        self.__source = Source.autodetect(sourcefile)
        filename = os.path.basename(sourcefile)
        dirpath = os.path.dirname(sourcefile)
        outfile = os.path.join(dirpath, f'cmd_{filename}.txt')
        self.__source.run(outfile=outfile)
        with open(outfile, 'r') as f:
            self.__naive_commands = [cmd.strip() for cmd in f.readlines()]
        os.remove(outfile)
        self.__commands = [self.__parse(cmd) for cmd in self.__naive_commands]
        self.__counts = [self.__count(cmd) for cmd in self.__commands]
        self.__acc_counts = list(accumulate(self.__counts))

    @staticmethod
    def __parse(target: str) -> ParsedCommand:
        ans = []
        for cmd in target.split():
            arr_cmd = cmd.split(sep='..', maxsplit=1)
            if len(arr_cmd) == 1: ans.append(int(arr_cmd[0]))
            else:
                st = int(arr_cmd[0])
                ed = int(arr_cmd[1])
                if st >= ed: raise ValueError('Range Error')
                ans.append((st, ed))
        return ans
    
    @staticmethod
    def __count(target: ParsedCommand) -> int:
        cnt = 1
        for val in target:
            if type(val) == tuple:
                cnt *= val[1]-val[0]+1
        return cnt

    @staticmethod
    def __select(target: ParsedCommand) -> List[str]:
        ret = []
        for val in target:
            if type(val) == int: ret.append(val)
            else: ret.append(random.randint(val[0], val[1]))
        return [str(val) for val in ret]

    def pickCommand(self) -> List[str]:
        idx = random.randrange(0, self.__acc_counts[-1])
        cmd_idx = bisect.bisect_left(self.__acc_counts, idx)
        return self.__select(self.__commands[cmd_idx])
    
    def getCommands(self) -> List[str]:
        return self.__naive_commands

    def getFilepath(self) -> str:
        return self.__source.getFilepath()