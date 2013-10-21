import sys
import re

class ThunderbirdFilterImporter:
    actions = ["None", "MoveToFolder", "ChangePriority", "Delete", "MarkRead", 
               "KillThread", "WatchThread", "MarkFlagged", "Label", "Reply", +
               "Forward", "StopExecution", "DeleteFromPop3Server", "LeaveOnPop3Server", 
               "JunkScore", "FetchBodyFromPop3Server", "CopyToFolder", "AddTag", 
               "KillSubthread"]

    def __init__(self):
        pass

    def read(self, filename):
        f = open(filename)
        lines = f.readlines()
        act = [[x[0], x[1].strip().strip("\"")] for x in [line.split("=") for line in lines]]
        
        version = act.pop(0)
        logging = act.pop(0)
        filternum = 0
        while len(act) > 1:
            for i in range(1, len(act)):
                if act[i][0] == "name": break
            curset = act[:i]
            for i in range(i): act.pop(0)
            if len(act) == 1:
                curset.append(act.pop(0))
            print "======================================"
            filternum += 1
            filtername = ""
            filteractions = ""
            filterconditions = ""
            filterenabled = True
            for key, value in curset:
                if key == "name":
                    filtername = value
                    print filtername
                elif key == "type":
                    # We ignore "type"
                    continue
                elif key == "condition":
                    print "Unrolling condition: %s" % value
                    res = re.split("((AND|OR) \(([\w\s]+),([\w\s]*),(.*)\)[\s]*)+", value)
                    print res

                elif key == "enabled":
                    if value == "no": filterenabled = False
                elif key == "action":
                    currentaction = value
                    print "FOOO: %s = %s" % (key, value)
                elif key == "actionValue":
                    if currentaction == "Move to Folder":
                        pass
                    print "BAAR: %s = %s" % (key, value)
                else:
                    raise Exception("Error parsing %s = %s" % (key, value))

            if filterenabled:
                print "filter:%d = %s" % (filternum, filtername)
                print "filter_tags:%d = %s" % (filternum, filteractions)
                print "filter_terms:%d = %s" % (filternum, filterconditions)




if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Need more arguments!"
        sys.exit()

    t = ThunderbirdFilterImporter()
    t.read(sys.argv[1])
