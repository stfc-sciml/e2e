# Tutorial

## Pre-processing

The preprocessing component of the pipeline consists of two stages, extraction and HDF conversion. 

### Extraction
 The extraction step unzips the raw data from the CEDA archive. The extraction step takes an input list of file locations on the CEDA archive and will unzip every file in the list to the corresponding output directory. An example of how to run this step is given below:

```bash
python e2e_benchmark/command.py extract file_list.txt extracted_files
```

### HDF Conversion

The HDF conversion converts the raw data files into a stand alone HDF file. This collects all of the brightness temperature channels, radiance channels, and product masks into a single file. This step is neccesary to cut down the number of I/O calls during training. This step also converts the radiance channels to reflectance values. An example of how to run this step is given below:

```bash
python e2e_benchmark/command.py convert_hdf extracted_files hdf_files
```

## Training

## Post-processing
