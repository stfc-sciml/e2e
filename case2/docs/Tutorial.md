# Pipeline Components

![pipeline](case2/docs/pipeline.png "pipeline")
Diagram of the full end-to-end workflow of the benchmark. Red components indicate the artifacts input or output from each stage. Blue components indicate a step in the processing workflow.

### Software
The benchmark is written in pure python code. The preprocessing scripts make use of the NetCDF, H5py, and scikit-image libraries pre-processing the imagry. The network uses a U-Net style architecture with 9 channels as input (6 channels reflectance, 3 channels brightness temperature) and a single channel binary output. This network is written in Tensorflow 2.0. A full list of software requirements can be found in the [requirements.txt](case2/requirements.txt)

### Timings
Rough timings for a single run of each stage on an single DGX-2 node with a single v100 GPU.

| Stage                       | Time (s)           | Notes                                       |
|-----------------------------|--------------------|---------------------------------------------|
| Convert to HDF (Train)      | 9099.09            |                                             |
| Convert to HDF (Validation) | 947.84             |                                             |
| Training (Total 30 epochs)  | 4674.06            |                                             |
| Training (1 Epoch)          | 142.89             | Time after tf.data.Dataset.cache            |
| Training (1 Epoch Train)    | 124.19             | Time after tf.data.Dataset.cache            |
| Training (1 Epoch Test)     | 18.70              | Time after tf.data.Dataset.cache            |
| Training (1st Epoch)        | 530.04             | Time before tf.data.Dataset.cache           |
| Training (1st Epoch Train)  | 431.11             | Time before tf.data.Dataset.cache           |
| Training (1st Epoch Test)   | 98.92              | Time before tf.data.Dataset.cache           |
| Inference                   | 118.40             |                                             |
| SST Comparision             | 1.10               |                                             |
| **Total**                   | 14840.49           |                                             |



### Extraction
 The extraction step unzips the raw data from the CEDA archive. The extraction step takes an input list of file locations on the CEDA archive and will unzip every file in the list to the corresponding output directory. An example of how to run this step is given below:

```bash
python -m e2e_benchmark.command extract file_list.txt extracted_files
```

### HDF Conversion

The HDF conversion converts the raw NetCDF files into a stand alone HDF file. This collects all of the brightness temperature channels, radiance channels, and product masks into a single file. This step is neccesary to cut down the number of I/O calls during training. This step also converts the radiance channels to reflectance values and resizes the images to a common size. Finally, the data will be split into day and night time image folders. An example of how to run this step is given below:

```bash
python -m e2e_benchmark.command convert_hdf extracted_files hdf_files
```

## Training
To train the model you will need to have performed both preprocessing tasks and should now have a folder to HDF files ready. The input parameters for the model training are the folder of HDF files and an output path to save the model to. This will run the U-net like model with each of the images in the input folder. The input images will be automatically split into a training & test set.

```bash
python -m e2e_benchmark.command train hdf_files model_output
```

To run the model in CPU only mode you can pass the additional flag `--cpu-only`. 

As part of a the data loading the following operations will be performed:

 - Image normaisation of each channel
 - Conversion from full (1500x1200) resolution to patches (512x512).
 - Cache these operations in memory using `tf.data.Dataset.cache`

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
