import os

class EtcHoster:
    """Utility class to manage adding/removing lines from /etc/hosts corresponding
    to an application name.  Only attempts to modify /etc/hosts if the user running
    the program has permission to do so; otherwise, silently does nothing."""
    def __init__(self, appname):
        self.appname = appname
        self.appline = "127.0.0.1    %s    # this line written by nappl" % appname
        self.etchosts = "/etc/hosts"
    def add_line(self):
        """Add the line for this app to /etc/hosts, if one is not already there."""
        if not os.access(self.etchosts, os.W_OK):
            return
        haveline = False
        # store all the lines, without newlines
        with open(self.etchosts, "r") as f:
            lines = [x.strip("\n") for x in f.readlines()]
        # check to see if we have a line for this app
        for line in lines:
            if line == self.appline:
                haveline = True
                break
        # if we didn't, write all the lines, followed by our app line
        if not haveline:
            with open(self.etchosts, "w") as f:
                for line in lines:
                    f.write(line + "\n")
                f.write(self.appline + "\n")
    def remove_lines(self):
        """Remove all lines corresponding to this app from /etc/hosts."""
        if not os.access(self.etchosts, os.W_OK):
            return
        changed = False
        # read and store all the lines, without newlines
        with open(self.etchosts, "r") as f:
            lines = [x.strip("\n") for x in f.readlines()]
        changed = False
        lines2 = []
        # copy them into lines2 array, skipping any that match our app line
        for line in lines:
            if line == self.appline:
                changed = True
            else:
                lines2.append(line)
        # if we skipped any lines, write the lines2 lines to the file
        if changed:
            with open(self.etchosts, "w") as f:
                for line in lines2:
                    f.write(line + "\n")
