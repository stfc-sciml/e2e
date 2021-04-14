# Pipeline Components

![pipeline](case2/docs/pipeline.png "pipeline")
Diagram of the full end-to-end workflow of the benchmark. Red components indicate the artifacts input or output from each stage. Blue components indicate a step in the processing workflow.

### Software
The benchmark is written in pure python code. The preprocessing scripts make use of the NetCDF, H5py, and scikit-image libraries pre-processing the imagry. The network uses a U-Net style architecture with 9 channels as input (6 channels reflectance, 3 channels brightness temperature) and a single channel binary output. This network is written in Tensorflow 2.0. A full list of software requirements can be found in the [requirements.txt](case2/requirements.txt)

### Timings
Rough timings for a single run of each stage on an single DGX-2 node with a single v100 GPU. *Note*: This implementation uses `tf.data.Dataset.cache` to store loaded data in memory after loading, so the first epoch takes longer than all subsequent epochs. The difference in time is noted below.

| Stage                       | Time (s)           | 
|-----------------------------|--------------------|
| Convert to HDF (Train)      | 9099.09            |
| Convert to HDF (Validation) | 947.84             |
| SST Comparision             | 1.10               |
| **Total**                   | 10048.03           |

Below shows the detailed training & inference performance across different systems and configurations.

#### PEARL

##### Training

| index     | system | num_ranks | num_gpus | total_time  | first_epoch_time | second_epoch_time | first_epoch_train_time | second_epoch_train_time | first_epoch_test_time | second_epoch_test_time | imgs_per_s_second_epoch | imgs_per_s_first_epoch | train_accuracy | test_accuracy | train_loss   | test_loss    | batch_size | epochs | learning_rate |
|-----------|--------|-----------|----------|-------------|------------------|-------------------|------------------------|-------------------------|-----------------------|------------------------|-------------------------|------------------------|----------------|---------------|--------------|--------------|------------|--------|---------------|
| run_24409 | PEARL  |         1 |        1 | 4686.985232 |      487.8024068 |        141.622344 |            397.6475568 |             121.4117088 |           90.14920092 |            20.20682693 |             159.7868952 |            48.78692115 |   0.8525564075 |  0.8511553407 |  0.212181896 | 0.2179534435 |         32 |     30 |         0.001 |
| run_24410 | PEARL  |         2 |        2 | 3681.385369 |      491.1161945 |       111.7994499 |            403.2262571 |             95.93596053 |           87.87036061 |            15.84929371 |             202.2182286 |            48.11194623 |   0.8602660298 |  0.8509029746 |  0.209066987 | 0.2072046548 |         32 |     30 |         0.001 |
| run_24411 | PEARL  |         4 |        4 |  1828.20399 |      247.7779794 |       56.72645378 |            207.1155813 |             50.34581685 |           40.65675735 |            6.377050877 |              385.334894 |            93.66750623 |   0.8714677691 |  0.8823924065 | 0.1888048351 |   0.19068937 |         32 |     30 |         0.001 |
| run_24412 | PEARL  |         8 |        8 | 1014.694396 |      147.2587397 |       30.28834724 |            125.2010143 |             26.60576439 |           22.05094743 |            3.679215431 |             729.1652935 |            154.9508214 |    0.870210588 |  0.8634964824 | 0.1910666525 | 0.2004272044 |         32 |     30 |         0.001 |
| run_24413 | PEARL  |        16 |       16 | 562.1420362 |      122.4123983 |       16.82446599 |            108.0181093 |              14.6912303 |           14.37209558 |            2.129650831 |             1320.515682 |            179.5995146 |   0.8498619795 |  0.8233401775 | 0.2154550254 | 0.2386761159 |         32 |     30 |         0.001 |

##### Inference

| index     | system | num_gpus | num_ranks | total       | imgs_per_s  |
|-----------|--------|----------|-----------|-------------|-------------|
| run_24409 | PEARL  |        1 |         1 | 1255.247758 | 1.593310951 |
| run_24410 | PEARL  |        2 |         2 | 1256.608641 | 1.591585427 |
| run_24411 | PEARL  |        4 |         4 | 539.1232088 | 3.709727141 |
| run_24412 | PEARL  |        8 |         8 | 265.4282806 |  7.53499211 |
| run_24413 | PEARL  |       16 |        16 | 153.5484927 | 13.02520113 |

#### SCARF

##### Training

| index     | system | num_gpus | num_ranks | total_time  | first_epoch_time | second_epoch_time | first_epoch_train_time | second_epoch_train_time | first_epoch_test_time | second_epoch_test_time | imgs_per_s_second_epoch | imgs_per_s_first_epoch | train_accuracy | test_accuracy | train_loss   | test_loss    | batch_size | epochs | learning_rate |
|-----------|--------|----------|-----------|-------------|------------------|-------------------|------------------------|-------------------------|-----------------------|------------------------|-------------------------|------------------------|----------------|---------------|--------------|--------------|------------|--------|---------------|
| run_53428 | SCARF  |        1 |         1 | 45402.69838 |      1544.732399 |       1385.684085 |            1310.427494 |             1135.814839 |            234.288147 |            249.8591855 |             17.08024877 |            14.80432919 |   0.8453990817 |  0.8437467813 | 0.2220225632 | 0.2172799259 |         32 |     30 |         0.001 |
| run_53429 | SCARF  |        2 |         2 | 23281.76684 |      887.9685924 |       758.1281309 |            768.9431183 |             605.4871981 |           119.0109875 |            152.6255419 |             32.04031408 |            25.22943445 |   0.8685059547 |  0.8409053683 |  0.199012056 | 0.2114881426 |         32 |     30 |         0.001 |
| run_53430 | SCARF  |        4 |         4 | 12457.26462 |       553.053158 |        430.865139 |            428.0327735 |             337.2702899 |           125.0028179 |            93.57313132 |             57.52063132 |            45.32363221 |   0.8864958882 |  0.8918270469 | 0.1738203466 | 0.1762486845 |         32 |     30 |         0.001 |
| run_53431 | SCARF  |        4 |         8 | 4786.609712 |      271.2817438 |       227.4275584 |            221.4258764 |             182.9286768 |           49.82610321 |            44.30622077 |             106.0522622 |            87.61396959 |   0.8920868039 |  0.9006774426 |  0.168565765 | 0.1690753251 |         32 |     30 |         0.001 |
| run_53432 | SCARF  |        4 |        16 |  1615.83125 |      138.0618007 |       49.79375076 |            117.5387204 |             42.28568292 |           20.50362778 |            7.483509541 |             458.7841241 |            165.0519926 |   0.8876604438 |   0.893393755 | 0.1764502972 | 0.1759866029 |         32 |     30 |         0.001 |
| run_53433 | SCARF  |        4 |        32 | 1006.319253 |        184.39413 |       26.36715484 |            150.9293756 |             22.45009375 |           33.44167328 |            3.885875463 |             864.1389305 |            128.5369393 |    0.877099812 |  0.8711004853 | 0.1782446504 | 0.1876683086 |         32 |     30 |         0.001 |

##### Inference

| index     | system | num_gpus | num_ranks | total       | imgs_per_s  |
|-----------|--------|----------|-----------|-------------|-------------|
| run_53428 | SCARF  |        1 |         1 | 1494.222932 | 1.338488359 |
| run_53429 | SCARF  |        2 |         2 | 1048.268264 | 1.907908566 |
| run_53430 | SCARF  |        4 |         4 | 664.9484975 | 3.007751739 |
| run_53431 | SCARF  |        4 |         8 | 297.8718445 | 6.714296892 |
| run_53432 | SCARF  |        4 |        16 | 111.2567739 | 17.97643352 |
| run_53433 | SCARF  |        4 |        32 | 78.90235639 | 25.34778544 |

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
