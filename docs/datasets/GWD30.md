---
Product Type: Sentinel & Machine Learning
Resolution (m): "30"
Year Range: 2013-2022
Article Link: https://doi.org/10.12436/GWD30.60.20250703
Dynamic: true
Classification: true
Time Resolution: 4 days (starting from January 1st, every 4 days)
Spatial Range: Global
---
## **Description**

  The Global Wetland Dynamics data (GWD30) is the first global wetland dynamics dataset with 30 m spatial resolution and near-daily (4-day interval) temporal frequency spanning from 2013 to 2024, derived from the global 30-m Seamless Data Cube (SDC) surface reflectance dataset and advanced machine learning and deep learning algorithms. GWD30 captures fine-scale, near-daily wetland fluctuations across the globe over more than a decade.

## **Tiling System**

 The dataset adopts a tiling scheme based on the UTM-based Military Grid Reference System (MGRS), consistent with the spatial structure used in ESA’s Sentinel-2 and NASA’s HLS products (Claverie et al., 2018). However, a slight modification was applied: to correct for the 15-meter (half-pixel) offset between the original Landsat coordinate system and the Sentinel-2 grid, we expanded and shifted the standard MGRS grid by 15 meters in both the X and Y directions. The SDC data is thus gridded into this adjusted MGRS framework, with each tile measuring 109.83 × 109.83 km, equivalent to 3661 × 3661 Landsat pixels.


## Classification Index
| Value | Class                       |
| ----- | --------------------------- |
| 0     | Non-wetland                 |
| 1     | River                       |
| 2     | Canal/Channel               |
| 3     | Lake                        |
| 4     | Reservoir/Pond              |
| 5     | Estuary Water               |
| 6     | Lagoon                      |
| 7     | Aquaculture Pond / Salt Pan |
| 8     | Inland Marsh                |
| 9     | Inland Swamp                |
| 10    | Floodplain                  |
| 11    | Coastal Marsh               |
| 12    | Coastal Swamp               |
| 13    | Tidal Flat                  |
| 14    | Shallow Marine Water        |
