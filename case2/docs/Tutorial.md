# Pipeline Components

### Extraction
 The extraction step unzips the raw data from the CEDA archive. The extraction step takes an input list of file locations on the CEDA archive and will unzip every file in the list to the corresponding output directory. An example of how to run this step is given below:

```bash
python -m e2e_benchmark.command extract file_list.txt extracted_files
```

### HDF Conversion

The HDF conversion converts the raw data files into a stand alone HDF file. This collects all of the brightness temperature channels, radiance channels, and product masks into a single file. This step is neccesary to cut down the number of I/O calls during training. This step also converts the radiance channels to reflectance values. Finally, the data will be split into day and night time image folders. An example of how to run this step is given below:

```bash
python -m e2e_benchmark.command convert_hdf extracted_files hdf_files
```

## Training
To train the model you will need to have performed both preprocessing tasks and should now have a folder to HDF files ready. The input parameters for the model training are the folder of HDF files and an output path to save the model to.

```bash
python -m e2e_benchmark.command train hdf_files model_output
```

To run the model in CPU only mode you can pass the additional flag `--cpu-only`.

### Inference
After the model has been trained you can run it on a set of test images using the inference command. The inference command takes three arguments:
 - The model file containing a trained model.
 - The data directory containing preprocessed HDF data to perform inference on
 - An output directory to predicted masks to for each image in the data directory

An example of how to run this step is given below:

```bash
python -m e2e_benchmark.command inference model_output/model_file.h5 hdf_files predictions
```

### SST Comparision
The final step of the benchmark is to compare the masked pixels in the validation SST dataset against the reference SST temperature buoys. For this you will specifically need the preprocessed ssts dataset. This step will take the table of SST match ups and compare the masks output from the model with those match ups and output the median and robust standard deviation for the match ups. An example of how to run this step is given below:

```bash
python -m e2e_benchmark.command sst_comp sst_matchups.h5 predictions
```
