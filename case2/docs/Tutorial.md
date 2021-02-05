# Pipeline Components

![pipeline](case2/docs/pipeline.png "pipeline")
Diagram of the full end-to-end workflow of the benchmark. Red components indicate the artifacts input or output from each stage. Blue components indicate a step in the processing workflow.

### Software
The benchmark is written in pure python code. The preprocessing scripts make use of the NetCDF, H5py, and scikit-image libraries pre-processing the imagry. The network uses a U-Net style architecture with 9 channels as input (6 channels reflectance, 3 channels brightness temperature) and a single channel binary output. This network is written in Tensorflow 2.0. A full list of software requirements can be found in the [requirements.txt](case2/requirements.txt)

### Timings
Rough timings for a single run of each stage on an single DGX-2 node with a single v100 GPU. *Note*: This implementation uses `tf.data.Dataset.cache` to store loaded data in memory after loading, so the first epoch takes longer than all subsequent epochs. The difference in time is noted below.

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

Below shows the detailed training performance across different systems and configurations.

| System | Job ID | # Nodes | # GPUs | Cache? | Epochs | Total Time(s) | Time 1 Epoch (s) | Train Time 1 Epoch (s) | Test Time 1 Epoch (s) | Time 1st Epoch (s) | Train time 1st Epoch | Test Time 1st Epoch | Accuracy | Loss    |
|--------|--------|---------|--------|--------|--------|---------------|------------------|------------------------|-----------------------|--------------------|----------------------|---------------------|----------|---------|
| PEARL  | 20176  | 1       | 1      | Y      | 30     | 4894.09       | 148.66           | 128.86                 | 19.80                 | 536.46             | 434.36               | 102.09              | 84%      | 0.23851 |
| PEARL  | 19974  | 1       | 2      | Y      | 30     | 11000.68      | 415.01           | 336.68                 | 78.33                 | 454.70             | 373.24               | 81.45               | 84%      | 0.25569 |
| PEARL  | 19975  | 1       | 4      | Y      | 30     | 5659.76       | 190.73           | 152.26                 | 38.47                 | 234.24             | 194.07               | 40.16               | 86%      | 0.20783 |
| PEARL  | 19976  | 1       | 8      | Y      | 30     | 2942.93       | 96.72            | 78.39                  | 18.33                 | 142.72             | 122.61               | 20.11               | 87%      | 0.21899 |
| PEARL  | 19995  | 1       | 16     | Y      | 30     | 535.37        | 15.03            | 13.68                  | 1.97                  | 117.48             | 102.68               | 14.79               | 83%      | 0.23977 |
|        |        |         |        |        |        |               |                  |                        |                       |                    |                      |                     |          |         |
| SCARF  | 789763 | 1       | 1      | N      | 30     | 40471.34      | 1530.06          | 1272.94                | 257.12                | n/a                | n/a                  | n/a                 | 84%      | 0.20906 |
| SCARF  | 789764 | 1       | 2      | N      | 30     | 25606.76      | 984.77           | 839.59                 | 145.17                | n/a                | n/a                  | n/a                 | 85%      | 0.21448 |
| SCARF  | 789765 | 1       | 4      | N      | 30     | 13638.27      | 581.85           | 438.32                 | 143.52                | n/a                | n/a                  | n/a                 | 89%      | 0.19948 |
|        |        |         |        |        |        |               |                  |                        |                       |                    |                      |                     |          |         |
| SCARF  | 789772 | 2       | 8      | N      | 30     | 4648.28       | 339.83           | 292.17                 | 47.65                 | n/a                | n/a                  | n/a                 | 90%      | 0.1643  |
| SCARF  | 789773 | 4       | 16     | N      | 30     | 1821.49       | 235.34           | 195.40                 | 39.93                 | n/a                | n/a                  | n/a                 | 90%      | 0.16477 |
| SCARF  | 790385 | 8       | 32     | N      | 30     | 2217.20       | 86.16            | 79.97                  | 6.18                  | n/a                | n/a                  | n/a                 | 84%      | 0.23107 |

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
