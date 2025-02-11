import sys



class Tee:
    """a tee-like behavior class to redirect stdout to a file.
    
    this code is adapted from stackoverflow.
    """
    def __init__(self, file_path):
        """initializes the tee object.
        
        @params:
        - file_path : string, path to the log file
        """
        self.terminal = sys.stdout
        self.log = open(file_path, "a", encoding="utf-8")  # specify encoding

    def write(self, message):
        """writes the message to both the terminal and the log file."""
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        """flushes both the terminal and the log file."""
        self.terminal.flush()
        self.log.flush()

    def __del__(self):
        """ensures the log file is properly closed when the object is destroyed."""
        self.log.close()
