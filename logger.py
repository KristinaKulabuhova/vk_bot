class Logger:
    def __init__(self, logfile):
        self.logfile = None
        self.logfile_name = logfile
        self.__clear_log()
        self.__open_log()
    
    def log(self, entry):
        if(self.logfile.tell() > 4 * 1024 * 1024):
            self.logfile.close()
            self.__clear_log()
            self.__open_log()

        self.logfile.write(entry + "\n")
    
    def __del__(self):
        self.logfile.close()

    def __clear_log(self):
        open(self.logfile_name, "w").close()

    def __open_log(self):
        self.logfile = open(self.logfile_name, "a")

