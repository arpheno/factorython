from pprint import pprint as print

import numpy as np

defaultCurve = [
	[0,0,0,0,0,1,0,0],
	[0,0,0,0,1,1,1,0],
	[0,0,0,1,1,1,1,0],
	[0,0,0,1,1,1,0,0],
	[0,0,1,1,1,0,0,0],
	[0,0,1,1,0,0,0,0],
	[0,0,1,1,0,0,0,0],
	[0,0,1,1,0,0,0,0],
]

def flipLR(a):
	return np.flip(np.array(a),1)
def flipDiag(a):
	return np.array(a).T
curve_map = [0] * 9
curve_map[1] = defaultCurve
curve_map[6] = flipDiag(curve_map[1])
curve_map[3] = flipLR(curve_map[6])
curve_map[4] = flipDiag(curve_map[3])
curve_map[5] = flipLR(curve_map[4])
curve_map[2] = flipDiag(curve_map[5])
curve_map[7] = flipLR(curve_map[2])
curve_map[8] = flipDiag(curve_map[7])
curve_map=[flipDiag(f) for f in curve_map]
#
# function getCurveMask(dir)
# local out = {}
# local map = table.deepcopy(curveMap[dir])
# local index = 1
# for r=1,8 do
#     for c=1,8 do
#          if map[r][c] == 1 then
#              out[index] = {["x"] = c-5, ["y"] = r-5}
#              index = index + 1
#          end
#     end
# end
# return out
# end
#
#
# local function flipDiag(input)
# local out = table.deepcopy(input)
# for r=1,8 do
#     for c=1,8 do
#          out[r][c] = input[c][r]
#     end
# end
# return out
# end
#
# curveMap = {}
# curveMap[1] = defaultCurve
# curveMap[6] = flipDiag(curveMap[1])
# curveMap[3] = flipLR(curveMap[6])
# curveMap[4] = flipDiag(curveMap[3])
# curveMap[5] = flipLR(curveMap[4])
# curveMap[2] = flipDiag(curveMap[5])
# curveMap[7] = flipLR(curveMap[2])
# curveMap[8] = flipDiag(curveMap[7])
#
# function getCurveMask(dir)
# local out = {}
# local map = table.deepcopy(curveMap[dir])
# local index = 1
# for r=1,8 do
#     for c=1,8 do
#          if map[r][c] == 1 then
#              out[index] = {["x"] = c-5, ["y"] = r-5}
#              index = index + 1
#          end
#     end
# end
# return out
# end