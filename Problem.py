# TODO Subtasks, Code Refactoring

import os
import json
import subprocess
import shutil
import datetime
from typing import Tuple, Union, Dict, List, Type
from subprocess import CalledProcessError
from Source import Source
from Checker import Checker, ValidatedScore
from Formatter import Formatter
from Controller import Controller
from Stress import Stress, StressJSON
from TestCase import TestCase

class ProblemBase():
    timelimit = None
    generator = None
    validator = None
    checker = Checker()
    solutions = []
    tests = []
    stresses = []

    def __init__(self, probtype: str, probpath: str) -> None:
        self.probtype = probtype
        self.probpath = os.path.abspath(probpath)
        if os.path.exists(self.probpath): self.importJSON()
        else: self.newProblem()
        
    def writeJSON(self) -> None:
        jsonobj = {}
        jsonobj['type'] = self.probtype
        jsonobj['timelimit'] = self.timelimit
        jsonobj['generator'] = None if (self.generator is None) else self.generator.getFilepath()
        jsonobj['validator'] = None if (self.validator is None) else self.validator.getFilepath()
        jsonobj['checker'] = self.checker.getFilepath()
        jsonobj['tests'] = self.tests
        jsonobj['solutions'] = [sol.getFilepath() for sol in self.solutions]
        jsonobj['stresses'] = [stress.exportJSON() for stress in self.stresses]
        with open(os.path.join(self.probpath, 'data.json'), 'w') as f:
            json.dump(jsonobj, f)
    
    def importJSON(self) -> None:
        with open(os.path.join(self.probpath, 'data.json'), 'r') as f:
            jsonobj = json.load(f)
        if self.probtype != jsonobj['type']: raise ValueError('Problem Type Is Not Correct')
        self.timelimit = None if (jsonobj['timelimit'] is None) else float(jsonobj['timelimit'])
        self.generator = None if (jsonobj['generator'] is None) else Source.autodetect(jsonobj['generator'])
        self.validator = None if (jsonobj['validator'] is None) else Source.autodetect(jsonobj['validator'])
        self.checker = Checker() if (jsonobj['checker'] is None) else Checker(filepath=jsonobj['checker'])
        self.tests = jsonobj['tests']
        self.solutions = [Source.autodetect(sol) for sol in jsonobj['solutions']]
        self.stresses = [Stress.importJSON(self, jsonval) for jsonval in jsonobj['stresses']]

    def newProblem(self) -> None:
        self.createFolder('TC')
        self.createFolder('Solutions')
        self.createFolder('Files')
        self.createFolder('Stresses')
        pythonpath = os.path.abspath(__file__)
        testlibpath = os.path.join(os.path.dirname(pythonpath), 'testlib.h')
        shutil.copyfile(testlibpath, os.path.join(self.probpath, 'Files', 'testlib.h'))
        self.writeJSON()
    
    def getFilepath(self, *args) -> str:
        return os.path.join(self.probpath, *args)

    def createFolder(self, dirpath: str) -> None:
        dirpath = self.getFilepath(dirpath)
        if not os.path.exists(dirpath): os.makedirs(dirpath)
    
    def setTimeLimit(self, timelimit: float) -> None:
        self.timelimit = timelimit
    
    def eraseTimeLimit(self) -> None:
        self.timelimit = None
    
    def copyFile(self, src: str, *args) -> str:
        filepath = self.getFilepath(dirname, *args)
        if os.path.exists(filepath): raise ValueError('Already Existing File')
        shutil.copyfile(os.path.abspath(src), filepath)
        return filepath

    def setGenerator(self, generator: str) -> None:
        genpath = self.copyFile(generator, 'Files', 'generator.cpp')
        self.generator = Source.autodetect(genpath)

    def setValidator(self, validator: str) -> None:
        valpath = self.copyFile(validator, 'Files', 'validator.cpp')
        self.validator = Source.autodetect(valpath)
        
    def setChecker(self, checker: str) -> None:
        chkpath = self.copyFile(checker, 'Files', 'checker.cpp')
        self.checker = Checker(filepath=chkpath)

    def eraseGenerator(self) -> None:
        self.generator = None

    def eraseValidator(self) -> None:
        self.validator = None

    def eraseChecker(self) -> None:
        self.checker = Checker()
    
    def addSolution(self, solution: str) -> None:
        solpath = self.copyFile(solution, 'Solutions', os.path.basename(solution))
        self.solutions.append(Source.autodetect(solpath))
    
    def addStress(self, solution_num: int, counters: int, runningtime: int, commandfile: str) -> None:
        dirpath = self.getFilepath('Stresses', )
        filepath = self.copyFile(commandfile, 'Stresses', os.path.basename(commandfile))
        self.stresses.append(Stress(self, solution_num, counters, runningtime, filepath))
    
    def runStress(self, stress_num: int) -> None:
        print(self.stresses[stress_num].run())

    def setMCS(self, num: int) -> None:
        self.solutions[0], self.solutions[num] = self.solutions[num], self.solutions[0]

    def genTC(self, tc_id: str, *args) -> None:
        if tc_id in self.tests: raise ValueError('Already Existing TestCase')
        if self.generator is None: raise ValueError('Generator Must Be Provided')
        if len(self.solutions) == 0: raise ValueError('Main Correct Soultion Must Be Provided')
        infile = os.path.join(self.probpath, 'TC', f'Input{tc_id}.txt')
        outfile = os.path.join(self.probpath, 'TC', f'Output{tc_id}.txt')
        self.generator.run(*args, outfile=infile)
        if self.validator is not None:
            try: self.validator.run(infile=infile, outfile=os.devnull, errfile=os.devnull)
            except CalledProcessError: raise ValueError('Wrong TestCase Generated')
        self.solutions[0].run(infile=infile, outfile=outfile, timeout=self.timelimit)
        self.tests.append(tc_id)
    
    def eraseTC(self, tc_id: str) -> None:
        if tc_id in self.tests:
            self.tests.remove(tc_id)
            infile = os.path.join(self.probpath, 'TC', f'Input{tc_id}.txt')
            outfile = os.path.join(self.probpath, 'TC', f'Output{tc_id}.txt')
            os.remove(infile)
            os.remove(outfile)
        else: raise ValueError('Not Existing TestCase')
    
    def scoring(self, solution_num: int, tc_id: str) -> ValidatedScore:
        if not tc_id in self.tests: raise ValueError('Not Existing TestCase')
        self.createFolder('Sandbox')
        infile = os.path.join(self.probpath, 'TC', 'Input{}.txt'.format(tc_id))
        outfile = os.path.join(self.probpath, 'Sandbox', 'Output{}.txt'.format(tc_id))
        ansfile = os.path.join(self.probpath, 'TC', 'Output{}.txt'.format(tc_id))
        self.solutions[solution_num].run(infile=infile, outfile=outfile, timeout=self.timelimit)
        score = self.checker.check(infile, outfile, ansfile)
        shutil.rmtree(os.path.join(self.probpath, 'Sandbox'))
        return score

class Batch(ProblemBase):
    def __init__(self, *args, **kwargs):
        super().__init__('Batch', *args, **kwargs)

p = Batch('Test')
'''
p.setGenerator('Test_prob/gen.cpp')
p.setValidator('Test_prob/val.cpp')
p.setChecker('Test_prob/chk.cpp')
p.addSolution('Test_prob/MCS.cpp')
p.addSolution('Test_prob/AC1.cpp')
p.addSolution('Test_prob/AC2.cpp')
p.addSolution('Test_prob/AC.py')
p.addSolution('Test_prob/WA1.cpp')
p.addSolution('Test_prob/WA2.cpp')
p.addStress(5, 10, 60, 'Test_prob/St.txt')
'''
'''
for i in range(1, 100):
    #p.genTC('1_{:02d}'.format(i), '1', str(i))
    for j in range(len(p.solutions)):
        print(p.scoring(j, '1_{:02d}'.format(i)), end='')
    print()
'''
p.runStress(0)
p.writeJSON()