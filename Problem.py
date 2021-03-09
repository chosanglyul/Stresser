# TODO Subtasks, Code Refactoring

import os
import json
import subprocess
import shutil
import datetime
from typing import Tuple, Union, Dict, List, Type
from Source import Source
from Checker import Checker, ValidatedScore
from Formatter import Formatter
from Controller import Controller
from Stress import Stress
from Generator import Generator
from TestCase import TestCase

class ProblemBase():
    timelimit = None
    generator = Generator()
    checker = Checker()
    solutions = []
    tests = []
    stresses = []

    def __init__(self, probtype: str, probpath: str) -> None:
        self.probtype = probtype
        self.probpath = os.path.abspath(probpath)
        if os.path.exists(self.probpath): self.readJSON()
        else: self.newProblem()

    def exportJSON(self):
        jsonobj = {
            'type': self.probtype,
            'timelimit': self.timelimit,
            'checker': self.checker.getFilepath(),
            'tests': self.tests,
            'generator': self.generator.exportJSON()
        }
        jsonobj['solutions'] = [sol.getFilepath() for sol in self.solutions]
        jsonobj['stresses'] = [stress.exportJSON() for stress in self.stresses]
        return jsonobj
        
    def writeJSON(self) -> None:
        with open(os.path.join(self.probpath, 'data.json'), 'w') as f:
            json.dump(self.exportJSON(), f)
    
    def importJSON(self, jsonobj) -> None:
        self.probtype = jsonobj['type']
        self.tests = jsonobj['tests']
        self.timelimit = None if (jsonobj['timelimit'] is None) else float(jsonobj['timelimit'])
        self.generator.importJSON(jsonobj['generator'])
        self.checker = Checker(filepath=jsonobj['checker'])
        self.solutions = [Source.autodetect(sol) for sol in jsonobj['solutions']]
        self.stresses = [Stress.importJSON(self, jsonval) for jsonval in jsonobj['stresses']]
    
    def readJSON(self) -> None:
        with open(os.path.join(self.probpath, 'data.json'), 'r') as f:
            jsonobj = json.load(f)
        self.importJSON(jsonobj)

    def newProblem(self) -> None:
        self.createFolder('Solutions')
        self.createFolder('Files')
        self.createFolder('Stresses')
        pythonpath = os.path.abspath(__file__)
        testlibpath = os.path.join(os.path.dirname(pythonpath), 'testlib.h')
        self.copyFile(testlibpath, 'Files', 'testlib.h')
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
        filepath = self.getFilepath(*args)
        if os.path.exists(filepath): raise ValueError('Already Existing File')
        shutil.copyfile(os.path.abspath(src), filepath)
        return filepath

    def setGenerator(self, generator: str) -> None:
        genpath = self.copyFile(generator, 'Files', 'generator.cpp')
        self.generator.setGenerator(genpath)

    def setValidator(self, validator: str) -> None:
        valpath = self.copyFile(validator, 'Files', 'validator.cpp')
        self.generator.setValidator(valpath)
        
    def setChecker(self, checker: str) -> None:
        chkpath = self.copyFile(checker, 'Files', 'checker.cpp')
        self.checker = Checker(filepath=chkpath)

    def eraseGenerator(self) -> None:
        self.generator.eraseGenerator()

    def eraseValidator(self) -> None:
        self.generator.eraseValidator()

    def eraseChecker(self) -> None:
        self.checker = Checker()
    
    def addSolution(self, solution: str) -> None:
        solpath = self.copyFile(solution, 'Solutions', os.path.basename(solution))
        self.solutions.append(Source.autodetect(solpath))
    
    def addStress(self, solution_num: int, counters: int, runningtime: int, commandfile: str) -> None:
        #dirpath = self.getFilepath('Stresses', )
        filepath = self.copyFile(commandfile, 'Stresses', os.path.basename(commandfile))
        self.stresses.append(Stress(self, solution_num, counters, runningtime, filepath))
    
    def addTestCase(self, command):
        parsed_cmd = Controller.parse_single(command)
        self.tests.append(parsed_cmd)
    
    def runStress(self, stress_num: int) -> None:
        print(self.stresses[stress_num].run())

    def setMCS(self, num: int) -> None:
        self.solutions[0], self.solutions[num] = self.solutions[num], self.solutions[0]

    def genTC(self, idx: int) -> None:
        if len(self.solutions) == 0: raise ValueError('Main Correct Soultion Must Be Provided')
        infile = os.path.join(self.probpath, 'TC', f'Input{idx}.txt')
        outfile = os.path.join(self.probpath, 'TC', f'Output{idx}.txt')
        self.generator.genTC(infile, *self.tests[idx])
        self.solutions[0].run(infile=infile, outfile=outfile, timeout=self.timelimit)

    def eraseTC(self, tc_id: str) -> None:
        if tc_id in self.tests:
            self.tests.remove(tc_id)
            os.remove(self.getFilepath('TC', f'Input{tc_id}.txt'))
            os.remove(self.getFilepath('TC', f'Output{tc_id}.txt'))
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
p.addSolution('Test_prob/AC.py')
p.addSolution('Test_prob/MCS.cpp')
p.addSolution('Test_prob/AC1.cpp')
p.addSolution('Test_prob/AC2.cpp')
p.addSolution('Test_prob/WA1.cpp')
p.addSolution('Test_prob/WA2.cpp')
p.addStress(5, 10, 60, 'Test_prob/St.txt')
p.writeJSON()

for i in range(1, 100):
    #p.genTC('1_{:02d}'.format(i), '1', str(i))
    for j in range(len(p.solutions)):
        print(p.scoring(j, '1_{:02d}'.format(i)), end='')
    print()
'''
p.runStress(0)
p.writeJSON()