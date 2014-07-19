var sensors = {

	site: "grenoble",
	archi: "m3",

	get: function(i) {
		var xy = this.xy[i];
		return {
			x: 20 + xy[0] * 20,
			y: 30 + 550 - xy[1] * 20,
			name: "m3-" + i
		}
	},

	"lines": {
		"h1": [94, 70, -1],
		"h2": [1, 69, +1],
		"v11": [95, 177, +2],
		"v12": [96, 178, +2],
		"v21": [289, 205, -2],
		"v22": [288, 204, -2],
		"h3": [179, 203, +1],
		"h4": [290, 358, +1],
		"h5": [359, 380, +1],
	},

	"xy": {

1: [20.10, 26.76],
2: [20.70, 26.76],
3: [21.30, 26.76],
4: [21.90, 26.76],
5: [22.50, 26.76],
6: [23.10, 26.76],
7: [24.55, 26.76],
8: [25.15, 26.76],
9: [25.75, 26.76],
10: [26.35, 26.76],
11: [26.95, 26.76],
12: [27.55, 26.76],
13: [28.15, 26.76],
14: [28.75, 26.76],
15: [29.35, 26.76],
16: [29.95, 26.76],
17: [30.55, 26.76],
18: [31.15, 26.76],
19: [31.75, 26.76],
20: [32.35, 26.76],
21: [32.95, 26.76],
22: [33.55, 26.76],
23: [34.15, 26.76],
24: [34.75, 26.76],
25: [35.35, 26.76],
26: [35.95, 26.76],
27: [36.55, 26.76],
28: [37.15, 26.76],
29: [37.75, 26.76],
30: [38.35, 26.76],
31: [38.95, 26.76],
32: [39.55, 26.76],
33: [40.15, 26.76],
34: [40.75, 26.76],
35: [41.35, 26.76],
36: [41.95, 26.76],
37: [42.55, 26.76],
38: [43.15, 26.76],
39: [43.75, 26.76],
40: [44.35, 26.76],
41: [44.95, 26.76],
42: [45.55, 26.76],
43: [46.15, 26.76],
44: [46.75, 26.76],
45: [47.35, 26.76],
46: [47.95, 26.76],
47: [48.55, 26.76],
48: [49.15, 26.76],
49: [49.75, 26.76],
50: [50.35, 26.76],
51: [50.95, 26.76],
52: [51.55, 26.76],
53: [52.15, 26.76],
54: [52.75, 26.76],
55: [53.35, 26.76],
56: [53.95, 26.76],
57: [54.55, 26.76],
58: [55.15, 26.76],
59: [55.75, 26.76],
60: [56.35, 26.76],
61: [56.95, 26.76],
62: [57.55, 26.76],
63: [58.15, 26.76],
64: [58.75, 26.76],
65: [59.35, 26.76],
66: [59.95, 26.76],
67: [60.55, 26.76],
68: [61.15, 26.76],
69: [61.75, 26.76],
70: [17.02, 26.76],
71: [16.42, 26.76],
72: [15.82, 26.76],
73: [15.22, 26.76],
74: [14.62, 26.76],
75: [14.02, 26.76],
76: [13.42, 26.76],
77: [12.82, 26.76],
78: [12.22, 26.76],
79: [11.62, 26.76],
80: [11.02, 26.76],
81: [10.42, 26.76],
82: [9.82, 26.76],
83: [9.22, 26.76],
84: [8.62, 26.76],
85: [8.02, 26.76],
86: [7.42, 26.76],
87: [6.82, 26.76],
88: [6.22, 26.76],
89: [5.62, 26.76],
90: [5.02, 26.76],
91: [4.42, 26.76],
92: [3.82, 26.76],
93: [3.22, 26.76],
94: [2.62, 26.76],
95: [0.40, 26.52],
96: [1.00, 26.52],
97: [0.40, 25.92],
98: [1.00, 25.92],
99: [0.40, 25.23],
100: [1.00, 25.23],
101: [0.40, 24.63],
102: [1.00, 24.63],
103: [0.40, 24.03],
104: [1.00, 24.03],
105: [0.40, 23.43],
106: [1.00, 23.43],
107: [0.40, 22.83],
108: [1.00, 22.83],
109: [0.40, 22.23],
110: [1.00, 22.23],
111: [0.40, 21.63],
112: [1.00, 21.63],
113: [0.40, 21.03],
114: [1.00, 21.03],
115: [0.40, 20.43],
116: [1.00, 20.43],
117: [0.40, 19.83],
118: [1.00, 19.83],
119: [0.40, 19.23],
120: [1.00, 19.23],
121: [0.40, 18.63],
122: [1.00, 18.63],
123: [0.40, 18.03],
124: [1.00, 18.03],
125: [0.40, 17.43],
126: [1.00, 17.43],
127: [0.40, 16.83],
128: [1.00, 16.83],
129: [0.40, 16.23],
130: [1.00, 16.23],
131: [0.40, 15.63],
132: [1.00, 15.63],
133: [0.40, 15.03],
134: [1.00, 15.03],
135: [0.40, 14.43],
136: [1.00, 14.43],
137: [0.40, 13.83],
138: [1.00, 13.83],
139: [0.40, 13.23],
140: [1.00, 13.23],
141: [0.40, 12.63],
142: [1.00, 12.63],
143: [0.40, 12.03],
144: [1.00, 12.03],
145: [0.40, 11.43],
146: [1.00, 11.43],
147: [0.40, 10.83],
148: [1.00, 10.83],
149: [0.40, 10.23],
150: [1.00, 10.23],
151: [0.40, 9.63],
152: [1.00, 9.63],
153: [0.40, 9.03],
154: [1.00, 9.03],
155: [0.40, 8.43],
156: [1.00, 8.43],
157: [0.40, 7.83],
158: [1.00, 7.83],
159: [0.40, 7.23],
160: [1.00, 7.23],
161: [0.40, 6.63],
162: [1.00, 6.63],
163: [0.40, 6.03],
164: [1.00, 6.03],
165: [0.40, 5.43],
166: [1.00, 5.43],
167: [0.40, 4.83],
168: [1.00, 4.83],
169: [0.40, 4.23],
170: [1.00, 4.23],
171: [0.40, 3.63],
172: [1.00, 3.63],
173: [0.40, 3.03],
174: [1.00, 3.03],
175: [0.40, 2.43],
176: [1.00, 2.43],
177: [0.40, 1.85],
178: [1.00, 1.85],
179: [2.75, 0.94],
180: [3.35, 0.94],
181: [3.95, 0.94],
182: [4.55, 0.94],
183: [5.15, 0.94],
184: [5.75, 0.94],
185: [6.35, 0.94],
186: [6.95, 0.94],
187: [7.55, 0.94],
188: [8.15, 0.94],
189: [8.75, 0.94],
190: [9.35, 0.94],
191: [9.95, 0.94],
192: [10.55, 0.94],
193: [11.15, 0.94],
194: [11.75, 0.94],
195: [12.35, 0.94],
196: [12.95, 0.94],
197: [13.55, 0.94],
198: [14.15, 0.94],
199: [14.75, 0.94],
200: [15.35, 0.94],
201: [15.95, 0.94],
202: [16.55, 0.94],
203: [17.15, 0.94],
204: [18.95, 0.75],
205: [18.35, 0.75],
206: [18.95, 1.83],
207: [18.35, 1.83],
208: [18.95, 2.43],
209: [18.35, 2.43],
210: [18.95, 3.03],
211: [18.35, 3.03],
212: [18.95, 3.63],
213: [18.35, 3.63],
214: [18.95, 4.23],
215: [18.35, 4.23],
216: [18.95, 4.83],
217: [18.35, 4.83],
218: [18.95, 5.43],
219: [18.35, 5.43],
220: [18.95, 6.03],
221: [18.35, 6.03],
222: [18.95, 6.63],
223: [18.35, 6.63],
224: [18.95, 7.23],
225: [18.35, 7.23],
226: [18.95, 7.83],
227: [18.35, 7.83],
228: [18.95, 8.43],
229: [18.35, 8.43],
230: [18.95, 9.03],
231: [18.35, 9.03],
232: [18.95, 9.63],
233: [18.35, 9.63],
234: [18.95, 10.23],
235: [18.35, 10.23],
236: [18.95, 10.83],
237: [18.35, 10.83],
238: [18.95, 11.43],
239: [18.35, 11.43],
240: [18.95, 12.03],
241: [18.35, 12.03],
242: [18.95, 12.63],
243: [18.35, 12.63],
244: [18.95, 13.23],
245: [18.35, 13.23],
246: [18.95, 13.83],
247: [18.35, 13.83],
248: [18.95, 14.43],
249: [18.35, 14.43],
250: [18.95, 15.03],
251: [18.35, 15.03],
252: [18.95, 15.63],
253: [18.35, 15.63],
254: [18.95, 16.23],
255: [18.35, 16.23],
256: [18.95, 16.83],
257: [18.35, 16.83],
258: [18.95, 17.43],
259: [18.35, 17.43],
260: [18.95, 18.03],
261: [18.35, 18.03],
262: [18.95, 18.63],
263: [18.35, 18.63],
264: [18.95, 19.23],
265: [18.35, 19.23],
266: [18.95, 19.83],
267: [18.35, 19.83],
268: [18.95, 20.43],
269: [18.35, 20.43],
270: [18.95, 21.03],
271: [18.35, 21.03],
272: [18.95, 21.63],
273: [18.35, 21.63],
274: [18.95, 22.23],
275: [18.35, 22.23],
276: [18.95, 22.83],
277: [18.35, 22.83],
278: [18.95, 23.43],
279: [18.35, 23.43],
280: [18.95, 24.03],
281: [18.35, 24.03],
282: [18.95, 24.63],
283: [18.35, 24.63],
284: [18.95, 25.23],
285: [18.35, 25.23],
286: [18.95, 26.00],
287: [18.35, 26.00],
288: [18.95, 26.52],
289: [18.35, 26.52],
290: [20.05, 0.94],
291: [20.65, 0.94],
292: [21.25, 0.94],
293: [21.85, 0.94],
294: [22.45, 0.94],
295: [23.05, 0.94],
296: [24.62, 0.94],
297: [25.22, 0.94],
298: [25.85, 0.94],
299: [26.42, 0.94],
300: [27.02, 0.94],
301: [28.22, 0.94],
302: [28.71, 0.94],
303: [29.36, 0.94],
304: [29.96, 0.94],
305: [30.56, 0.94],
306: [31.16, 0.94],
307: [31.76, 0.94],
308: [32.36, 0.94],
309: [32.96, 0.94],
310: [33.56, 0.94],
311: [34.16, 0.94],
312: [34.76, 0.94],
313: [35.36, 0.94],
314: [35.96, 0.94],
315: [36.56, 0.94],
316: [37.16, 0.94],
317: [37.76, 0.94],
318: [38.36, 0.94],
319: [38.96, 0.94],
320: [39.56, 0.94],
321: [40.16, 0.94],
322: [40.76, 0.94],
323: [41.36, 0.94],
324: [41.96, 0.94],
325: [42.56, 0.94],
326: [43.16, 0.94],
327: [43.76, 0.94],
328: [44.36, 0.94],
329: [44.96, 0.94],
330: [45.56, 0.94],
331: [46.16, 0.94],
332: [46.76, 0.94],
333: [47.36, 0.94],
334: [47.96, 0.94],
335: [48.56, 0.94],
336: [49.16, 0.94],
337: [49.76, 0.94],
338: [50.36, 0.94],
339: [50.96, 0.94],
340: [51.56, 0.94],
341: [52.16, 0.94],
342: [52.76, 0.94],
343: [53.36, 0.94],
344: [53.96, 0.94],
345: [54.56, 0.94],
346: [55.16, 0.94],
347: [55.76, 0.94],
348: [56.36, 0.94],
349: [56.96, 0.94],
350: [57.56, 0.94],
351: [58.16, 0.94],
352: [58.76, 0.94],
353: [59.36, 0.94],
354: [59.96, 0.94],
355: [60.56, 0.94],
356: [61.16, 0.94],
357: [61.76, 0.94],
358: [62.26, 0.94],
359: [34.75, 25.75],
360: [35.35, 25.75],
361: [35.95, 25.75],
362: [36.55, 25.75],
363: [37.75, 24.92],
364: [38.25, 24.92], // modified: was 37.75 24.92 (same xy as 363, z=3.23)
365: [38.95, 25.75],
366: [39.55, 25.75],
367: [40.15, 25.75],
368: [40.75, 25.75],
369: [41.35, 25.75],
370: [46.15, 25.75],
371: [46.75, 25.75],
372: [47.35, 25.75],
373: [47.95, 25.75],
374: [48.55, 25.75],
375: [49.15, 25.75],
376: [52.15, 25.75],
377: [52.75, 25.75],
378: [53.35, 25.75],
379: [53.95, 25.75],
380: [54.55, 25.75],
}
};
