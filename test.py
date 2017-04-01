import numpy as np
import matplotlib.pyplot as plt

values = []
lines  = []
with open('netValue.txt') as fp:
    logLines = 0
    for line in fp:
        lines.append(logLines)
        logLines += 1
        value = float(line)
        values.append(value)
        #print(value)

print(sorted(values, key=int)[-10:])
print(max(values))

#plt.plot(values)
plt.plot(lines,values)
plt.axis([0, len(lines), 100, 200000])
plt.show()


values = []
lines  = []
with open('log.txt') as fp:
    logLines = 0
    for line in fp:
        lines.append(logLines)
        logLines += 1
        value = line.split(":")[-1]
        value = float(value)
        values.append(value)
        #print(value)

print(sorted(values, key=int)[-10:])
print(max(values))

