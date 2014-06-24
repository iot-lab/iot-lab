"""
 Clusters of 8, co-located, valid nodes for GRE.

 Variables defined here provide groups (clusters) of 8 valid nodes.
 Nodes in the same cluster are physically co-located, so should
 hopefully have little to no problems communicating through radio.

 The list of valid nodes is copied from ``never dead nodes`` in gre.py.
 There is no guarantee that these nodes will in effect never die.

 Note: not all valid nodes are listed, as clusters specs require that
 a.) nodes are co-located and b.) there are exactly 8 nodes per cluster.
"""

cluster_gre_m3 = [ _.split() for _ in [
"9  10 11 13 14 15 17 18",
"20 21 23 24 25 28 29 30",
"31 32 33 35 36 37 38 39",
"40 41 44 45 46 47 48 49",
"51 55 59 61 63 65 68 69",
"2  4  5  6  8  71 72 73",
#77 80
"85  88  91  94  101 102 105 106",
"109 113 114 115 116 117 118 122",
"123 124 125 129 130 131 132 133",
"134 135 136 138 139 140 141 142",
"146 147 148 150 151 152 155 157",
"158 159 160 161 162 167 169 171",
"174 175 178 179 180 181 182 185",
"187 188 189 191 192 194 196 197",
"198 203 204 206 208 210 212 213",
"214 216 219 220 222 226 227 231",
"232 234 235 236 237 239 241 242",
"244 245 246 248 252 253 254 257",
"258 260 262 263 264 265 267 271",
"272 273 278 280 282 285 288 289",
"290 292 293 297 298 299 300 301",
"303 307 309 310 311 312 313 314",
"317 318 321 322 324 325 328 335",
"337 338 339 343 344 346 348 349",
#354 359 360 363 366 367
"368 371 374 375 376 377 379 380",
]]
