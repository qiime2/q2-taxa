import { select } from 'd3';

import init from './init';
import render from './render';
import { sort } from './data';


export const availableColorSchemes = [
  { name: 'PRGn', scheme: 'interpolatePRGn' },
  { name: 'BrBG', scheme: 'interpolateBrBG' },
  { name: 'PiYG', scheme: 'interpolatePiYG' },
  { name: 'PuOr', scheme: 'interpolatePuOr' },
  { name: 'RdBu', scheme: 'interpolateRdBu' },
  { name: 'RdGy', scheme: 'interpolateRdGy' },
  { name: 'RdYlBu', scheme: 'interpolateRdYlBu' },
  { name: 'RdYlGn', scheme: 'interpolateRdYlGn' },
  { name: 'Spectral', scheme: 'interpolateSpectral' },
];

// HELPERS
function _getSort(sel, svg, data, dataMeta) {
  const sorts = sel.selectAll('.xCtrl').nodes().map(d => d.options[d.selectedIndex].value);
  const orders = sel.selectAll('.xOrder').nodes().map(d => d.options[d.selectedIndex].value);
  const labels = sel.selectAll('.xLabel').nodes().map(d => (d.type === 'hidden' ? false : d.checked));
  return sort(data, sorts, orders, labels, dataMeta);
}

function _updateSort(sel, svg, data, dataMeta) {
  const xOrdering = _getSort(sel, svg, data, dataMeta);
  render(svg, svg.property('colorScheme'), xOrdering, dataMeta);
}

function _appendSortByPicker(sel, svg, data, dataMeta) {
  const row = sel.append('div').attr('class', 'row');
  const lcol = row.append('div').attr('class', 'col-lg-4');
  const mcol = row.append('div').attr('class', 'col-lg-4');
  const rcol = row.append('div').attr('class', 'col-lg-4');

  const sortBySelect = lcol.append('select').attr('class', 'xCtrl form-control')
    .on('change', function sortChange() {
      rcol.select('label').remove();

      const currentSelect = select(this).node();
      const key = currentSelect.options[currentSelect.selectedIndex].value;
      const keyIsMetaData = dataMeta.metaData.indexOf(key) > -1;

      rcol.append('label')
        .text(() => (keyIsMetaData ? 'Relabel X? ' : ''))
        .append('input')
        .attr('class', 'xLabel')
        .attr('type', () => (keyIsMetaData ? 'checkbox' : 'hidden'))
        .property('checked', true)
        .on('change', () => {
          _updateSort(sel, svg, data, dataMeta);
        });

      _updateSort(sel, svg, data, dataMeta);
    });
  const ordering = ['Ascending', 'Descending'];
  mcol.append('select').attr('class', 'xOrder form-control')
    .on('change', () => { _updateSort(sel, svg, data, dataMeta); })
    .selectAll('option')
    .data(ordering)
    .enter()
      .append('option')
      .attr('value', d => d)
      .text(d => d);
  return sortBySelect;
}

function _sortBySelectOptions(sel, keys, defaultOptionName) {
  const update = sel.selectAll('option').data(keys, d => d);
  update.exit().remove();
  const enter = update.enter().append('option');
  return update.merge(enter)
    .attr('value', d => d)
    .property('selected', d => (d === defaultOptionName))
    .text(d => d);
}

export function addTaxaPicker(row, levels, selectedLevel) {
  const grp = row.append('div').attr('class', 'col-lg-2 form-group taxaPicker');
  grp.append('label').text('Taxonomic Level');
  grp.append('select')
    .attr('class', 'form-control')
    .on('change', function appendTaxaPicker() {
      const body = select('body');
      body.select('.container-fluid').remove();
      body.insert('div', ':first-child').attr('class', 'container-fluid');
      init(this.selectedIndex);
    })
    .selectAll('option')
    .data(levels)
    .enter()
      .append('option')
        .attr('value', d => d)
        .text(d => d)
        .property('selected', d => (d === selectedLevel));
  return grp;
}

export function addColorPicker(row, svg, data, dataMeta) {
  const grp = row.append('div').attr('class', 'col-lg-2 form-group colorPicker');
  grp.append('label').text('Color Palette');
  grp.append('select')
    .attr('class', 'form-control')
    .on('change', function changeColorPicker() {
      const colorScheme = this.options[this.selectedIndex].value;
      const xOrdering = _getSort(row, svg, data, dataMeta);
      render(svg, colorScheme, xOrdering, dataMeta);
    })
    .selectAll('option')
    .data(availableColorSchemes)
    .enter()
      .append('option')
        .attr('value', d => d.scheme)
        .text(d => d.name);
  return grp;
}

export function addSortByPicker(row, svg, data, dataMeta) {
  const grp = row.append('div').attr('class', 'col-lg-6 form-group sortByPicker');
  grp.append('label').text('Sort By');
  grp.append('button').text('+')
    .attr('class', 'btn btn-primary btn-xs')
    .style('margin-left', '10px')
    .on('click', () => {
      const keys = [...dataMeta.metaData, ...dataMeta.sortedKeysReverse];
      const selects = grp.selectAll('.xCtrl');
      if (selects.size() === keys.length + 1) { return; }
      const sel = _appendSortByPicker(grp, svg, data, dataMeta);
      _sortBySelectOptions(sel, keys, dataMeta.sortedKeys[0]);
    });
  // Add initial 'Sort By' to sortByGroup
  const sel = _appendSortByPicker(grp, svg, data, dataMeta);
  const keys = [...dataMeta.metaData, ...dataMeta.sortedKeysReverse];
  _sortBySelectOptions(sel, keys, dataMeta.sortedKeys[0]);
  return grp;
}

export function addDownloadLinks(sel, svg) {
  const grp = sel.append('div').attr('class', 'col-lg-2 form-group');
  grp.append('label').html('&nbsp;');
  grp.append('button')
    .text('Download SVG')
    .attr('class', 'btn btn-default form-control')
    .on('click', () => {
      /* global XMLSerializer */
      const serializer = new XMLSerializer();
      let src = serializer.serializeToString(svg.node());
      src = `<?xml version="1.0" standalone="no"?>\r\n${src}`;
      const url = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(src)}`;

      /* global document */
      const link = document.createElement('a');
      link.setAttribute('href', url);
      link.setAttribute('download', 'taxaplot.svg');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
}
