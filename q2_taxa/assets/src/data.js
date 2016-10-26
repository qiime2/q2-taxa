import {
  stack,
  stackOffsetExpand,
  stackOrderAscending,
  ascending,
  descending,
} from 'd3';
import naturalSort from 'natural-sort';
import firstBy from 'thenby';


function _stableAscending(a, b, key) {
  const aVal = a[key];
  const bVal = b[key];
  if (aVal === bVal) {
    return ascending(a.position, b.position);
  }
  return naturalSort({ direction: 'asc' })(aVal, bVal);
}

function _ascending(a, b, key) {
  return naturalSort({ direction: 'asc' })(a[key], b[key]);
}

function _stableDescending(a, b, key) {
  const aVal = a[key];
  const bVal = b[key];
  if (aVal === bVal) {
    return descending(a.position, b.position);
  }
  return naturalSort({ direction: 'desc' })(aVal, bVal);
}

function _descending(a, b, key) {
  return naturalSort({ direction: 'desc' })(a[key], b[key]);
}

function _getRelative(a, b, key) {
  const aRel = a[key] / a.total;
  const bRel = b[key] / b.total;
  return { aRel, bRel };
}

function _stableSortAscRelative(a, b, key) {
  const { aRel, bRel } = _getRelative(a, b, key);
  if (aRel === bRel) {
    return ascending(a.position, b.position);
  }
  return ascending(aRel, bRel);
}

function _sortAscRelative(a, b, key) {
  const { aRel, bRel } = _getRelative(a, b, key);
  return ascending(aRel, bRel);
}

function _stableSortDescRelative(a, b, key) {
  const { aRel, bRel } = _getRelative(a, b, key);
  if (aRel === bRel) {
    return descending(a.position, b.position);
  }
  return descending(aRel, bRel);
}

function _sortDescRelative(a, b, key) {
  const { aRel, bRel } = _getRelative(a, b, key);
  return descending(aRel, bRel);
}

function _computeTotal(data, keys) {
  for (let i = 0; i < data.length; i += 1) {
    const sample = data[i];
    let t = 0;
    for (let j = 0; j < keys.length; j += 1) {
      t += sample[keys[j]];
    }
    sample.total = t;
    sample.position = i;
  }
}

export function sort(data, keys, orders, labels, dataMeta) {
  let sortStack = firstBy(() => 0);
  let sorter;
  keys.forEach((key, i) => {
    const isLastSorter = i === keys.length - 1;
    const order = orders[i];
    const isMetaData = dataMeta.metaData.indexOf(key) > -1;
    let func;

    if (isLastSorter && order === 'Ascending') {
      func = isMetaData ? _stableAscending : _stableSortAscRelative;
    } else if (isLastSorter && order === 'Descending') {
      func = isMetaData ? _stableDescending : _stableSortDescRelative;
    } else if (!isLastSorter && order === 'Ascending') {
      func = isMetaData ? _ascending : _sortAscRelative;
    } else if (!isLastSorter && order === 'Descending') {
      func = isMetaData ? _descending : _sortDescRelative;
    }

    sorter = (a, b) => func(a, b, key);
    sortStack = sortStack.thenBy(sorter);
  });

  const sortMap = {};
  const sortedSampleIDs = data.sort(sortStack).map((d) => {
    const _first = d[dataMeta.first];
    const newLabel = [];
    keys.forEach((key, i) => { if (labels[i]) { newLabel.push(d[key]); } });
    sortMap[_first] = newLabel.length === 0 ? _first : newLabel.join('; ');
    return _first;
  });
  return { sortedSampleIDs, sortMap };
}

export function setupData(data, svg) {
  const levelData = data.data;
  const keys = data.taxaKeys;
  const columns = JSON.parse(JSON.stringify(levelData.columns));
  let sortedKeys;
  let sortedKeysReverse;
  const metaData = columns.filter(i => keys.indexOf(i) < 0);
  const first = columns.splice(0, 1)[0];
  svg.property('firstTaxa', first);

  const dataStack = stack()
    .keys(keys)
    .order((series) => {
      const stackOrder = stackOrderAscending(series);
      sortedKeys = new Array(stackOrder.length);
      stackOrder.forEach((sortKey, i) => { sortedKeys[i] = keys[sortKey]; });
      sortedKeysReverse = sortedKeys.slice().reverse();
      svg.property('stackOrder', stackOrder);
      return stackOrder;
    })
    .offset(stackOffsetExpand); // Normalizes the rendered bars

  const layers = dataStack(levelData);
  _computeTotal(levelData, keys);

  /* global d */
  const levels = d.map(d => d.name);

  return {
    keys,
    columns,
    metaData,
    sortedKeys,
    sortedKeysReverse,
    first,
    layers,
    levels,
  };
}
