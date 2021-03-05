class Formatter():
    @staticmethod
    def transform(filename: str) -> None:
        with open(filename, 'r') as f:
            texts = f.readlines()
        lstline = -1
        for i in range(len(texts)):
            texts[i] = texts[i].strip() + '\n'
            if texts[i] != '\n': lstline = i
        with open(filename, 'w') as f:
            for line in texts[:lstline+1]:
                f.write(line)