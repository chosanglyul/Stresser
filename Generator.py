import os
from typing import Type, Dict, Union
from Source import Source
from subprocess import CalledProcessError
GeneratorJSON = Dict[str, Union[str, None]]

class Generator():
    __generator = None
    __validator = None
    
    def exportJSON(self) -> GeneratorJSON:
        jsonobj = {}
        jsonobj['generator'] = None if (self.__generator is None) else self.__generator.getFilepath()
        jsonobj['validator'] = None if (self.__validator is None) else self.__validator.getFilepath()
        return jsonobj
    
    def importJSON(self, jsonobj: GeneratorJSON) -> None:
        self.setGenerator(jsonobj['generator'])
        self.setValidator(jsonobj['validator'])
    
    def setGenerator(self, filepath: str) -> None:
        self.__generator = Source.autodetect(filepath)
    
    def setValidator(self, filepath: str) -> None:
        self.__validator = Source.autodetect(filepath)
    
    def eraseGenerator(self) -> None:
        self.__generator = None
    
    def eraseValidator(self) -> None:
        self.__validator = None

    def getGenerator(self) -> Type[Source]:
        return self.__generator
    
    def getValidator(self) -> Type[Source]:
        return self.__validator

    def genTC(self, infile: str, *args) -> None:
        if self.__generator is None: raise ValueError('Generator Must Be Provided')
        self.__generator.run(*args, outfile=infile)
        if self.__validator is not None:
            try: self.__validator.run(infile=infile)
            except CalledProcessError: raise ValueError('Wrong TestCase Generated')