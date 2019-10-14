import {
  scaleOrdinal,
  scaleBand,
  scaleLinear,
  scaleSequential,
  axisBottom,
  axisLeft,
  format,
} from 'd3';

import { setupXAxis, setupYAxis } from './axis';
import plotBars from './bar';
import { availableColorSchemes } from './toolbar';

export const transitionDur = 500;

export default function render(svg, colorScheme, xOrdering, dataMeta, barWidth) {
  const { sortMap, sortedSampleIDs } = xOrdering;
  const width = sortedSampleIDs.length * barWidth;
  const height = 600;
  const margin = { top: 20, left: 60, right: 0, bottom: 50 };
  const { keys } = dataMeta;
  const chart = svg.select('g');

  svg.property('colorScheme', colorScheme);

  const x = scaleBand().padding(0.1).domain(sortedSampleIDs).range([0, width]);
  const y = scaleLinear().domain([0, 1]).range([height, 0]).nice();
  const scheme = availableColorSchemes.find(s => (s.name === colorScheme));
  let z;
  if (scheme.type === 's') {
    z = scaleSequential(scheme.scheme).domain([0, keys.length - 1]);
  } else if (scheme.type === 'o') {
    const temp = scheme.scheme.reverse();
    const range = [];
    const domain = [];
    for (let i = 0; i < keys.length; i += 1) {
      range.push(temp[i % scheme.scheme.length]);
      domain.push(i);
    }
    z = scaleOrdinal(range).domain(domain);
    scheme.scheme.reverse();
  }

  const xAxis = axisBottom();
  const yAxis = axisLeft();

  xAxis.scale(x).tickFormat(d => sortMap[d]);
  yAxis.scale(y).tickFormat(format('.0%'));

  chart.attr('transform', `translate(${margin.left},${margin.top})`);

  const maxLabelX = setupXAxis(svg, chart, width, height, xAxis);
  setupYAxis(svg, chart, height, yAxis);

  plotBars(chart, x, y, z, dataMeta, sortMap);

  const newWidth = width + margin.left + margin.right;
  const newHeight = height + margin.top + margin.bottom + maxLabelX;

  // Resize canvas as needed
  svg
    .attr('width', newWidth)
    .attr('height', newHeight);

  const stackOrder = svg.property('stackOrder');
  return { keys, z, stackOrder, newHeight };
}
