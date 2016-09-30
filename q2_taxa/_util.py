def _extract_to_level(taxonomy, table, max_level=None):
    # Assemble the taxonomy data
    taxa = {}
    for k, v in taxonomy.to_dict().items():
        taxa[k] = {'taxonomy': [x.strip() for x in v.split(';')]}
    table.add_metadata(taxa, axis='observation')

    # Pluck first to determine depth.
    # TODO: Is it safe to assume that the depth will be the same for
    # each sample?
    max_obs_level = len(list(taxa.values())[0]['taxonomy'])

    if max_level is None:
        max_level = max_obs_level

    if max_level > max_obs_level:
        raise ValueError('Requested max_level of %d is larger than max_level '
                         'available in taxonomy data (%d).' % (max_level,
                                                               max_obs_level))

    collapsed_tables = []
    # Collapse table at specified level
    for level in range(1, max_level + 1):
        def bin_f(id_, x):
            return ';'.join(x['taxonomy'][:level])
        collapsed_tables.append(table.collapse(bin_f, norm=False,
                                               min_group_size=1,
                                               axis='observation'))

    return collapsed_tables
