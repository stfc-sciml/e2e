# Datasets

Three datasets are provided with this benchmark. The details of each induvidual dataset are given in the table below. Each dataset contains multiple folders refered to as level 1 Sentinel-3 SLSTR products. Each product contains multiple data files containing the raw brightness temperatures and radiances measured by the satellite. For more details on the specific contains of the level 1 products, the reader is referered to the [SLSTR level 1 handbook](https://sentinel.esa.int/documents/247904/1872792/Sentinel-3-SLSTR-Product-Data-Format-Specification-Level-1).


| Dataset | No. Products | Size (GB) | Description                                                                                                                                      |
|---------|--------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| one-day | 971          | 599       | Data recorded during a single full orbit cycle of Sentinel-3A. Consists of day and night time examples and images from a wide variety of biomes. |
| pixbox  | 414          | 243       | A mix of data used as part of a cloud mask validation dataset containing numerous difficult examples across a variety of biomes.                 |
| ssts    | 100          | 63        | A dataset of products which have been co-aligned with sea surface temperature (SST) buoys. The matching pixels in these products can be used to  |