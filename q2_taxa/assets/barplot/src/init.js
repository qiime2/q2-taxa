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
  /* global d window */
  const data = d[level].data;

  // DOM
  const body = select('body .container-fluid');
  const plotRow = body.append('div').attr('class', 'viz row');
  const plotDiv = plotRow.append('div').attr('class', 'col-lg-12');
  const collapseButton = plotDiv
    .append('a')
      .attr('class', 'btn btn-default form-control')
      .attr('role', 'button')
      .attr('data-toggle', 'collapse')
      .attr('href', '#collapse')
      .text('Toggle Controls');
  const collapsePanel = plotDiv.append('div').attr('class', 'collapse in').attr('id', 'collapse');
  const controlsRow = collapsePanel.append('div').attr('class', 'controls row');
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
  const { sortedKeysReverse, levels } = dataMeta;

  const initialSort = sort(data, [sortedKeysReverse[0]], ['Ascending'], [false], dataMeta);
  render(svg, initialColorScheme, initialSort, dataMeta);

  const checkToggle = () => {
    collapseButton.style('display', window.innerWidth > 1199 ? 'none' : 'inline-block');
    collapsePanel.attr('class', window.innerWidth > 1199 ? 'collapse.in' : 'collapse');
  };

  select(window).on('resize', checkToggle);

  // Controls
  const ctrlRowOne = controls.append('div').attr('class', 'row');
  checkToggle();
  addDownloadLinks(ctrlRowOne, svg);
  addTaxaPicker(ctrlRowOne, levels, d[level].name);
  addColorPicker(ctrlRowOne, svg, data, dataMeta);
  addSortByPicker(ctrlRowOne, svg, data, dataMeta);
}
