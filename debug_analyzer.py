import matplotlib.pyplot as plt
import json

data = json.load(open("out.json"))


start = data["x"][0]
t = [(t-start) / 1e9 for t in data["x"]]
data1 = [t / 1e6 for t in data["y1"]]
data2 = data["y2"]

x2 = data["x2"]
y3 = data["y3"]

#plt.scatter(data2, data1)

ax1 = plt.subplot(2, 1, 1)
ax = plt.subplot(2, 1, 2)

# per bullet
ax.scatter(data2, data1)
ax.set_xlabel("n (bullets")
ax.set_ylabel("t per iteration (ms)")

# per time
color = 'tab:red'
ax1.set_xlabel('time (s)')
ax1.set_ylabel('t (iteration) ms', color=color)
ax1.plot(t, data1, color=color)
axy.plot(y2, x3)
ax1.tick_params(axis='y', labelcolor=color)

plt.grid()

ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:blue'
ax2.set_ylabel('n (bullets)', color=color)  # we already handled the x-label with ax1
ax2.plot(t, data2, color=color)
ax2.tick_params(axis='y', labelcolor=color)

plt.grid()
#fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.tight_layout()
plt.show()
