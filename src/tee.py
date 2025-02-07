import sys



"""Tee
this is a tee-like behavior class to redirect stdout to a file.
this code is from `stackoverflow`.
"""
class Tee:
    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.log = open(file_path, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()
