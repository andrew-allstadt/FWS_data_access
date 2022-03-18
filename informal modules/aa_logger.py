# Simple log class for use in this module
import sys
import datetime


class Logger:
    def __init__(self, loggerFile, fileAccess='w', verbose=True):
        # Check value and try to open file
        if loggerFile is None or not isinstance(loggerFile, str):
            raise ValueError("Logger: loggerFile must be a string.")
        if fileAccess not in ['w', 'a']:
            raise ValueError("Logger: fileAccess must be 'w' (write) or 'a' (append).")

        # Will raise an exception itself if filepath not found.
        self.loggerFile = open(loggerFile, fileAccess)
        self.verbose = verbose
        self.isOpen = True
        self.name = self.loggerFile.name
        self.fileAccess = fileAccess
        self.arcpyLoaded = "arcpy" in sys.modules

        # Write opening message
        self.write_message("Opened file with fileAccess: " + self.fileAccess)

    def is_open(self):
        return self.isOpen

    def reopen(self):
        """
        Always reopen as append
        """
        if not self.isOpen:
            self.loggerFile = open(self.name, 'a')
            self.write_message("Reopened file with fileAccess: append")

    def close(self):
        if self.isOpen:
            self.write_message("Closing file.")
            self.loggerFile.close()
            self.isOpen = False
        return

    def write_message(self, message):
        """
        Nothing special, just option to print a message to standard IO as well as write it to file.
        :param self:
        :param message:
        :return: None (no return)
        """
        if message is None:
            return
        elif not isinstance(message, str):
            raise ValueError("Logger: message must be a valid string, or None for no effect.")

        appended_message = "[" + datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S") + "]: " + message

        if appended_message.find("\n") < 0:
            appended_message = appended_message + "\n"
        self.loggerFile.write(appended_message)
        if self.verbose:
            print("Log: " + appended_message)
        return