import { select } from 'd3';

import render from './render';
import {
  availableColorSchemes,
  addTaxaPicker,
  addColorPicker,
  addSortByPicker,
  addDownloadLinks,
} from './toolbar';
import { setupData, sort } from './data';


export default function init(level) {
  /* global d */
  const data = d[level].data;

  // DOM
  const body = select('body .container-fluid');
  const plotRow = body.append('div').attr('class', 'viz row');
  const plotDiv = plotRow.append('div').attr('class', 'col-lg-12');
  const controlsRow = plotDiv.append('div').attr('class', 'controls row');
  const controls = controlsRow.append('div').attr('class', 'col-lg-12');
  const svgRow = plotDiv.append('div').attr('class', 'plot row');
  const svgCol = svgRow.append('div').attr('class', 'col-md-12');
  const svg = svgCol.append('svg');
  const chart = svg.append('g');
  chart.append('g').attr('class', 'x axis');
  chart.append('g').attr('class', 'y axis');

  chart.append('text')
    .attr('id', 'y-label')
    .attr('text-anchor', 'middle')
    .style('font', '12px sans-serif')
    .text('Relative Frequency');

  chart.append('text')
    .attr('id', 'x-label')
    .attr('text-anchor', 'middle')
    .style('font', '12px sans-serif')
    .text('Sample');

  const initialColorScheme = availableColorSchemes[0].name;
  const dataMeta = setupData(d[level], svg);
  const { sortedKeys, levels } = dataMeta;

  const initialSort = sort(data, [sortedKeys[0]], ['Ascending'], [false], dataMeta);
  render(svg, initialColorScheme, initialSort, dataMeta);

  // Controls
  const ctrlRowOne = controls.append('div').attr('class', 'row');
  addDownloadLinks(ctrlRowOne, svg);
  addTaxaPicker(ctrlRowOne, levels, d[level].name);
  addColorPicker(ctrlRowOne, svg, data, dataMeta);
  addSortByPicker(ctrlRowOne, svg, data, dataMeta);
}
