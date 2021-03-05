import os
from typing import Union, Tuple
from Source import Source
ValidatedScore = Tuple[Union[int, float], str]

class Checker():
    def __init__(self, filepath: Union[None, str]=None) -> None:
        self.useWhiteDiff = (filepath is None)
        if self.useWhiteDiff: self.checker = self.WhiteDiff()
        else: self.checker = Source.autodetect(filepath)
    
    def getFilepath(self) -> Union[None, str]:
        return None if self.useWhiteDiff else self.checker.getFilepath()
    
    def check(self, infile: Union[None, str], outfile: str, ansfile: str) -> ValidatedScore:
        if self.useWhiteDiff:
            score = self.checker.compare(outfile, ansfile)
            if score == 0: return 0, 'translate:wrong'
            else: return 1, 'translate:success'
        else:
            dirname = os.path.dirname(outfile)
            file_out = os.path.join(dirname, 'score.txt')
            file_err = os.path.join(dirname, 'message.txt')
            self.checker.run(infile, ansfile, outfile, outfile=file_out, errfile=file_err)
            with open(file_out, 'r') as file_s: score = float(file_s.readline())
            with open(file_err, 'r') as file_m: message = file_m.readline().strip()
            return score, message

    class WhiteDiff():
        def compare(self, outfile: str, ansfile: str) -> Tuple[int, str]:
            with open(ansfile, 'r') as f:
                ans = f.readlines()
            with open(outfile, 'r') as f:
                out = f.readlines()
            if len(ans) != len(out): return 0
            for i in range(len(ans)):
                if ans[i] != out[i]: return 0
            return 1