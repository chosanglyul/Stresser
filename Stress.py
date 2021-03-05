StressJSON = Dict[str, Union[int, str]]

class Stress():
    def __init__(self, problem: Type[ProblemBase], solution_num: int, counters: int, runningtime: int, commandfile: str):
        self.__problem = problem
        self.__solution_num = solution_num
        self.__counters = counters
        self.__runningtime = runningtime
        self.__controller = Controller(commandfile)

    @staticmethod
    def importJSON(problem: Type[ProblemBase], jsonobj: StressJSON) -> 'Stress':
        solution_num = int(jsonobj['solution_num'])
        counters = int(jsonobj['counters'])
        runtime = int(jsonobj['runningtime'])
        return Stress(problem, solution_num, counters, runtime, jsonobj['commandfile'])

    def exportJSON(self) -> StressJSON:
        jsonval = {}
        jsonval['solution_num'] = self.__solution_num
        jsonval['counters'] = self.__counters
        jsonval['runningtime'] = self.__runningtime
        jsonval['commandfile'] = self.__controller.getFilepath()
        return jsonval

    def run(self) -> List[List[str]]:
        self.__problem.createFolder('Sandbox')
        sttime = datetime.datetime.now()
        runtime = datetime.timedelta(seconds=self.__runningtime)
        find_counter = []
        while (runtime > datetime.datetime.now()-sttime) and (len(find_counter) < self.__counters):
            infile = os.path.join(self.__problem.probpath, 'Sandbox', 'Input{}.txt'.format(len(find_counter)+1))
            outfile = os.path.join(self.__problem.probpath, 'Sandbox', 'Output{}.txt'.format(len(find_counter)+1))
            ansfile = os.path.join(self.__problem.probpath, 'Sandbox', 'Answer{}.txt'.format(len(find_counter)+1))
            args = self.__controller.pickCommand()
            print(args)
            self.__problem.generator.run(*args, outfile=infile)
            if self.__problem.validator is not None:
                try: self.__problem.validator.run(infile=infile, outfile=os.devnull, errfile=os.devnull)
                except CalledProcessError: raise ValueError('Wrong TestCase Generated')
            self.__problem.solutions[0].run(infile=infile, outfile=ansfile, timeout=self.__problem.timelimit)
            self.__problem.solutions[self.__solution_num].run(infile=infile, outfile=outfile, timeout=self.__problem.timelimit)
            score = self.__problem.checker.check(infile, outfile, ansfile)
            if score[0] == 0:
                shutil.copyfile(infile, os.path.join(self.__problem.probpath, 'TC', 'Input{}.txt'.format(len(find_counter)+1)))
                shutil.copyfile(ansfile, os.path.join(self.__problem.probpath, 'TC', 'Output{}.txt'.format(len(find_counter)+1)))
                find_counter.append(args)
        shutil.rmtree(os.path.join(self.__problem.probpath, 'Sandbox'))
        return find_counter