import os
from typing import Union, Dict
from Source import Source
from Checker import Checker, ValidatedScore

class TestCase():
    def __init__(self, command: str, gen: Source, mcs: Source, chk: Checker, val: Union[None, Source]=None) -> None:
        self.__command = command
        self.__generator = gen
        self.__validator = val
        self.__solution = mcs
        self.__checker = chk
    
    def generate(self, infile: str, ansfile: str) -> None:
        self.__generator.run(outfile=infile)
        if self.__validator is not None:
            try: self.__validator.run(infile=infile, outfile=os.devnull, errfile=os.devnull)
            except CalledProcessError: raise ValueError('Wrong TestCase Generated')
        self.__solution.run(infile=infile, outfile=ansfile)

    def evaluate(self, solution: Source, infile: str, outfile: str, ansfile: str, timelimit: float) -> ValidatedScore:
        solution.run(infile=infile, outfile=outfile, timeout=timelimit)
        return self.__checker.check(infile, outfile, ansfile)