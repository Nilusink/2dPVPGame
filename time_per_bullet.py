import matplotlib.pyplot as plt
import json


data = json.load(open("out.json"))


start = data["x"][0]
t = [(t-start) / 1e9 for t in data["x"]]
data1 = [t / 1e6 for t in data["y1"]]
data2 = data["y2"]

plt.scatter(data2, data1)

plt.ylabel("ms per iteration")
plt.xlabel("n (bullets)")

plt.grid()
# otherwise the right y-label is slightly clipped
plt.show()
