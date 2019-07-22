import { select } from 'd3';

import render from './render';
import {
  addTaxaPicker,
  addWidthSlider,
  addColorPicker,
  addSortByPicker,
  addDownloadLinks,
} from './toolbar';
import { setupData, sort } from './data';
import plotLegend from './legend';


/* Re-initializes the display.
 *
 * "state" is an object that should contain the following entries:
 *
 * level -- an integer indicating the currently selected index in the
 *          "Taxonomic Level" dropdown (starts at 0)
 *
 * colorScheme -- the name of the current color scheme
 *
 * barWidth -- an integer indicating the currently selected bar width value
 */
export default function init(state) {
  /* global d */
  const data = d[state.level].data;

  // DOM
  const body = select('body .container-fluid');
  const vizRow = body.append('div').attr('class', 'viz row');
  const vizDiv = vizRow.append('div').attr('class', 'col-lg-12');
  const controlsRow = vizDiv.append('div').attr('class', 'controls row');
  const controls = controlsRow.append('div').attr('class', 'col-lg-12');
  const detailsRow = vizDiv.append('div').attr('class', 'details row');
  detailsRow.append('div').attr('class', 'col-lg-12');
  const plotRow = vizDiv.append('div').attr('class', 'plot row');
  const barCol = plotRow.append('div').attr('class', 'bars');

  const svgBar = barCol.append('svg');
  const bars = svgBar.append('g');
  bars.append('g').attr('class', 'x axis');
  bars.append('g').attr('class', 'y axis');

  const legendCol = plotRow.append('div').attr('class', 'legend');
  legendCol.append('svg');

  bars.append('text')
    .attr('id', 'y-label')
    .attr('text-anchor', 'middle')
    .style('font', '12px sans-serif')
    .text('Relative Frequency');

  bars.append('text')
    .attr('id', 'x-label')
    .attr('text-anchor', 'middle')
    .style('font', '12px sans-serif')
    .text('Sample');

  const dataMeta = setupData(d[state.level], svgBar);
  const { sortedKeysReverse, levels } = dataMeta;

  const initialSort = sort(data, [sortedKeysReverse[0]], ['Ascending'], [false], dataMeta);
  const chartInfo = render(svgBar, state.colorScheme, initialSort, dataMeta, state.barWidth);

  plotLegend(legendCol, chartInfo);

  // Controls
  const ctrlRowOne = controls.append('div').attr('class', 'row');
  addDownloadLinks(ctrlRowOne, svgBar, legendCol.select('svg'), state.level + 1);
  addTaxaPicker(ctrlRowOne, levels, state.level + 1);
  addColorPicker(ctrlRowOne, svgBar, legendCol, data, dataMeta, state.colorScheme);
  addSortByPicker(ctrlRowOne, svgBar, data, dataMeta);
  addWidthSlider(ctrlRowOne, svgBar, data, dataMeta, state.barWidth);
}
