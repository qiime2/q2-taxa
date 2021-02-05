# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import setup, find_packages
import versioneer

setup(
    name="q2-taxa",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    author="Matthew Ryan Dillon",
    author_email="matthewrdillon@gmail.com",
    url="https://qiime2.org",
    license="BSD-3-Clause",
    description="Taxonomic analysis and visualization.",
    entry_points={
        "qiime2.plugins":
        ["q2-taxa=q2_taxa.plugin_setup:plugin"]
    },
    package_data={'q2_taxa': ['assets/barplot/index.html',
                              'assets/barplot/dist/*']},
    zip_safe=False,
)
