/* global d */
import { tsvParse } from 'd3';

import init from './init';

// Entrypoint: process data, run init
function type(data, _, keys) {
  const output = data;
  // Coerce the data to numbers.
  keys.forEach((key, i) => {
    if (i === 0) { return; }
    const original = data[keys[i]];
    const casted = +original;
    output[keys[i]] = isNaN(casted) || original === '' ? original : casted;
  });
  return output;
}

for (const set of d) {
  set.data = tsvParse(set.rawdata, type);
}

init(0);
