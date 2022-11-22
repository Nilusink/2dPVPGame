import json
import yaml
import sys

file = sys.argv[1]

print(f"{file=}")

inp = json.load(open(file, "r"))

yaml.dump(inp, open(file.replace(".json", ".yaml"), "w"))


#gerade = zahl % 2 == 0
#
#def antword(ans: str):
#    #ans = "y" | "n"
#    ans = ans == "y"
#    gerade == ans
