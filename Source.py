# TODO Multi File Compile (ex. grader, twostep)

import os
import platform
import subprocess
import shutil
from typing import Type, Union, IO, List
from Formatter import Formatter

class Source():
    @staticmethod
    def autodetect(filepath: Union[None, str]) -> 'Source':
        if filepath is None: return None
        name, ext = os.path.splitext(filepath)
        langname = ['.c', '.cpp', '.py', '.txt']
        langclass = [CSource, CppSource, PythonSource, TextSource]
        try: langidx = langname.index(ext)
        except ValueError: raise ValueError('Unexpected File Extension')
        return langclass[langidx](filepath)

    @staticmethod
    def __open_file(filepath: str, mode: str) -> Union[None, IO]:
        if filepath is None: return None
        else: return open(filepath, mode)
    
    def __init__(self, filepath: str, language: str) -> None:
        self.__language = language
        self.__filepath = os.path.abspath(filepath)
        self.__excutablepath = self.getExcutablepath()
        if not os.path.exists(self.getExcutablepath()):
            try: self.compile()
            except: raise ValueError('Compilation Error')
    
    def getLanguage(self) -> str:
        return self.__language

    def getFilepath(self) -> str:
        return self.__filepath

    def getExcutablepath(self) -> str:
        return self.getFilepath()
    
    def compile(self) -> None:
        pass

    def _run_command(self) -> List[str]:
        return [self.getExcutablepath()]
    
    def run(self, *args, infile: Union[None, str]=None, outfile: Union[None, str]=None, errfile: Union[None, str]=None, **kwargs) -> None:
        files = [Source.__open_file(infile, 'r'), Source.__open_file(outfile, 'w'), Source.__open_file(errfile, 'w')]
        subprocess.check_call([*self._run_command(), *args], stdin=files[0], stdout=files[1], stderr=files[2], **kwargs)
        for f in files:
            if f is not None: f.close()
        if outfile is not None: Formatter.transform(outfile)
        if errfile is not None: Formatter.transform(errfile)

class CSource(Source):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath, 'C')

    def getExcutablepath(self) -> str:
        execute, ext = os.path.splitext(self.getFilepath())
        if platform.system() == 'Windows': return f'{execute}.exe'
        else: return execute
    
    def compile(self) -> None:
        subprocess.check_call(['gcc', '-DEVAL', '-std=gnu11', '-O2', '-pipe', '-static', '-s', '-o', self.getExcutablepath(), self.getFilepath(), '-lm'])

class CppSource(Source):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath, 'C++')

    def getExcutablepath(self) -> str:
        execute, ext = os.path.splitext(self.getFilepath())
        if platform.system() == 'Windows': return f'{execute}.exe'
        else: return execute

    def compile(self) -> None:
        subprocess.check_call(['g++', '-DEVAL', '-std=gnu++11', '-O2', '-pipe', '-static', '-s', '-o', self.getExcutablepath(), self.getFilepath()])

class PythonSource(Source):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath, 'Python')

    def _run_command(self) -> List[str]:
        if platform.system() == 'Windows': return ['py', '-3', self.getExcutablepath()]
        else: return ['python3', self.getExcutablepath()]

class TextSource(Source):
    def __init__(self, filepath: str) -> None:
        super().__init__(filepath, 'Text')

    def run(self, *args, outfile: Union[None, str]=None, **kwargs) -> None:
        if outfile is None: raise ValueError('Output File Must Be Provided')
        shutil.copyfile(self.getExcutablepath(), outfile)
