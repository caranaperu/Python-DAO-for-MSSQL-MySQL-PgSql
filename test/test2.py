import os
print(os.environ)
print("\n\n")
print(os.getenv("TMP"))

#path = r'/home/carana'
#for root, dirs, files in os.walk(path):
#        print(root)


import subprocess
import sys
print(sys.executable)
print(sys.path)
print(sys.platform)
#subprocess.call(["ping", "www.yahoo.com"])


program = "kate"
process=subprocess.Popen(program)
code = process.wait()
print(code)

############################3333333
print("\n\n")

args = ["ping","-c 10", "www.yahoo.com"]
process = subprocess.Popen(args,
                           stdout=subprocess.PIPE)

data = process.communicate()
for line in data:
    print(line)