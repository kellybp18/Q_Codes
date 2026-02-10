# 3D Attenuation Tomography Code for "Attenuation Tomographic Mapping of Interplate Asperities in the Rupture Region of the 2015 $M_{w}$ 8.3 Illapel, Chile, Earthquake"

This repository contains the scripts and input files needed to create the 3D shear wave quality factor ($Q_{S}$) attenuation tomography for the 2015 $M_{w}$ Illapel earthquake rupture region, found in "Attenuation Tomographic Mapping of Interplate Asperities in the Rupture Region of the 2015 $M_{w}$ 8.3 Illapel, Chile, Earthquake" by Brian P. Kelly and Raymond M. Russo.

**Citation:** Brian P Kelly, R M Russo, Attenuation Tomographic Mapping of Interplate Asperities in the Rupture Region of the 2015 $M_{w}$ 8.3 Illapel, Chile, Earthquake, _Geophysical Journal International_, 2026;, ggag041, https://doi.org/10.1093/gji/ggag041


# How To Use

The repository contains three scripts:

**Master_Tomo_Build.py</u>**: Creates the 3D $Q_{S}$ tomography of the Illapel earthquake region. Accepts as input along-path $Q_{S}$ for 3852 viable soure-receiver paths from "data/q_database.csv" and inverts for $Q_{S}$ in 3D spatial grid. The bounds of this grid and the box size within the grid can be altered. Output file "qs_model.csv" contains the 3D tomography and helpful other metadata.

**_Please Note:_** This script will generate several intermediate .txt and .csv files in the "data/" directory that can be quite large (10s of GB) depending on the box size used. If this is an issue, comment these out or increase box size for lower resolution.

**Master_Analysis.py:** This script plots various relationships between variables relevant to the along-path $Q_{S}$ data used in the inversion. 

**q_database_stats.py:** This script creates correlation matrices of $Q_{S}$ and other variables, and histograms of along-path $Q_{S}$ and $Q_{S}$ in the 3D tomography.
