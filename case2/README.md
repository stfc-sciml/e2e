# Case 2

Contents:
 - [Installation](#installation)
 - [Running benchmarks](#running-benchmarks)
 - [Datasets](#datasets)
 - [Results](#results)

## Installation

This benchmark is written with Tensorflow & Horovod. Horovod requires `cmake` and `openmpi` to be available on the host machine. Please ensure these are installed and available on your system before installing the rest of the project dependancies.
 - Clone the repo
 - Install tensorflow & horovod
 - `pip` install the rest of the requirements
 
```bash
git clone git@github.com:stfc-sciml/e2e.git
cd e2e/case2
conda install -c anaconda tensorflow-gpu
pip install horovod
pip install -r requirements.txt
```

## Running Benchmarks

### Data Preparation

The following two steps are necessary to prepare the raw data for training and inference. A preprocessed version of all the datasets are provided with the data download. Therefore these steps may be skipped if you're only training or running a model.

#### Extraction
 The extraction step unzips the raw data from the CEDA archive. The extraction step takes an input list of file locations on the CEDA archive and will unzip every file in the list to the corresponding output directory. An example of how to run this step is given below:

```bash
python -m e2e_benchmark.command extract file_list.txt extracted_files
```

#### HDF Conversion

The HDF conversion converts the raw NetCDF files into a stand alone HDF file. This collects all of the brightness temperature channels, radiance channels, and product masks into a single file. This step is neccesary to cut down the number of I/O calls during training. This step also converts the radiance channels to reflectance values and resizes the images to a common size. Finally, the data will be split into day and night time image folders. An example of how to run this step is given below:

```bash
python -m e2e_benchmark.command convert_hdf extracted_files hdf_files
```

### Training
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

## Datasets

Three datasets are provided with this benchmark. The details of each induvidual dataset are given in the table below. Each dataset contains multiple folders refered to as level 1 Sentinel-3 SLSTR products. Each product contains multiple data files containing the raw brightness temperatures and radiances measured by the satellite. For more details on the specific contains of the level 1 products, the reader is referered to the [SLSTR level 1 handbook](https://sentinel.esa.int/documents/247904/1872792/Sentinel-3-SLSTR-Product-Data-Format-Specification-Level-1).


| Dataset | No. Products | Size (GB) | Description                                                                                                                                      |
|---------|--------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| one-day | 971          | 599       | Data recorded during a single full orbit cycle of Sentinel-3A. Consists of day and night time examples and images from a wide variety of biomes. |
| pixbox  | 414          | 243       | A mix of data used as part of a cloud mask validation dataset containing numerous difficult examples across a variety of biomes.                 |
| ssts    | 100          | 63        | A dataset of products which have been co-aligned with sea surface temperature (SST) buoys. The matching pixels in these products can be used to validate the quality of cloud masking |

In addition to each of these raw datasets, the data transformed preprocessed to the HDF format is also provided. This is the intermediate output after running `convert_to_hdf` on each of the `one-day` and `ssts` dataset. These intermediate files can be found in `./hdf` and are about ~30% the size of the original dataset.


## Results
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

#### EPCC - CLX

Training with and without intel optimized python & Tensorflow Cascade Lake architecture.

##### Training

| index     	| python  	| system 	| num_ranks 	| ntasks_per_node 	| total_time  	| first_epoch_time 	| second_epoch_time 	| first_epoch_train_time 	| second_epoch_train_time 	| first_epoch_test_time 	| second_epoch_test_time 	| imgs_per_s_second_epoch 	| imgs_per_s_first_epoch 	| train_accuracy 	| test_accuracy 	| train_loss   	| test_loss    	| epochs 	| learning_rate 	| batch_size 	|
|-----------	|---------	|--------	|-----------	|-----------------	|-------------	|------------------	|-------------------	|------------------------	|-------------------------	|-----------------------	|------------------------	|-------------------------	|------------------------	|----------------	|---------------	|--------------	|--------------	|--------	|---------------	|------------	|
| run_66576 	| vanilla 	| EPCC   	|         4 	|               4 	| 51649.54848 	|      1560.667577 	|       1637.915146 	|             1516.92256 	|             1599.991123 	|           43.72372866 	|            37.92036057 	|             12.12506727 	|            12.78905101 	|   0.8587064743 	|  0.8718251586 	|  0.208926335 	| 0.1854402572 	|     30 	|         0.001 	|         32 	|
| run_66577 	| vanilla 	| EPCC   	|         8 	|               4 	| 23524.96386 	|      772.7405717 	|       737.0023594 	|             749.136749 	|             718.0756278 	|           23.59759521 	|            18.91870904 	|             27.01665291 	|            25.89647354 	|   0.8742671609 	|  0.8700324297 	|   0.18431665 	|  0.214483723 	|     30 	|         0.001 	|         32 	|
| run_66578 	| vanilla 	| EPCC   	|        16 	|               4 	| 11379.68126 	|      399.2550464 	|       367.6282547 	|            385.5892556 	|             357.5608628 	|           13.65680671 	|            10.05389118 	|             54.25649734 	|            50.31260524 	|   0.8818459511 	|  0.8577045202 	| 0.1702739298 	| 0.2206094116 	|     30 	|         0.001 	|         32 	|
| run_66579 	| vanilla 	| EPCC   	|        32 	|               4 	| 8428.152408 	|      318.2785456 	|        274.759768 	|            297.2674124 	|             269.4334223 	|           20.99960542 	|            5.323489904 	|             72.00294541 	|            65.26110562 	|   0.8904289007 	|  0.8739011288 	| 0.1600992233 	| 0.1789171845 	|     30 	|         0.001 	|         32 	|
| run_66584 	| intel   	| EPCC   	|         4 	|               4 	| 43590.22756 	|      1294.335372 	|       1484.717762 	|            1202.352931 	|             1407.646065 	|           91.97278357 	|            77.05811429 	|              13.7818735 	|            16.13502948 	|   0.8662624359 	|  0.8827086687 	| 0.1937021464 	| 0.1819740385 	|     30 	|         0.001 	|         32 	|
| run_66585 	| intel   	| EPCC   	|         8 	|               4 	| 19652.99672 	|      649.8109686 	|        663.506371 	|            613.4108272 	|             634.0308509 	|           36.38298774 	|            29.47120309 	|             30.59788017 	|            31.62643883 	|   0.8770614862 	|  0.8737696409 	| 0.1836441159 	|  0.201986596 	|     30 	|         0.001 	|         32 	|
| run_66586 	| intel   	| EPCC   	|        16 	|               4 	| 10048.95009 	|      370.1908703 	|       325.2897694 	|             338.415674 	|              305.858561 	|           31.76151896 	|             19.4233954 	|             63.42801043 	|            57.32594998 	|   0.8748027682 	|  0.8450528383 	| 0.1811204255 	| 0.2225735188 	|     30 	|         0.001 	|         32 	|
| run_66587 	| intel   	| EPCC   	|        32 	|               4 	| 5018.560455 	|      180.0462604 	|       165.5005553 	|            168.0348213 	|             156.2506983 	|           12.00623393 	|            9.245760441 	|             124.1594451 	|            115.4522607 	|   0.8825953603 	|  0.8800027966 	| 0.1745795608 	| 0.1922903806 	|     30 	|         0.001 	|         32 	|


 <img src="https://user-images.githubusercontent.com/2487781/116727059-fcd9db80-a9db-11eb-977f-18755a3d433c.png" width=600 />
 <img src="https://user-images.githubusercontent.com/2487781/116727067-ff3c3580-a9db-11eb-8cc9-e6a688f355e1.png" width=600 />
 
##### Inference

| index     	| system 	| python  	| num_ranks 	| ntasks_per_node 	| total       	| imgs_per_s  	|
|-----------	|--------	|---------	|-----------	|-----------------	|-------------	|-------------	|
| run_66576 	| EPCC   	| vanilla 	|         4 	|               4 	| 200.0939715 	| 9.995303632 	|
| run_66577 	| EPCC   	| vanilla 	|         8 	|               4 	| 107.6166244 	| 18.58448926 	|
| run_66578 	| EPCC   	| vanilla 	|        16 	|               4 	| 59.96940947 	| 33.35033674 	|
| run_66579 	| EPCC   	| vanilla 	|        32 	|               4 	| 31.91276693 	| 62.67084281 	|
| run_66584 	| EPCC   	| intel   	|         4 	|               4 	| 257.3960884 	| 7.770125851 	|
| run_66585 	| EPCC   	| intel   	|         8 	|               4 	|  133.802573 	| 14.94739567 	|
| run_66586 	| EPCC   	| intel   	|        16 	|               4 	| 73.51474023 	| 27.20542838 	|
| run_66587 	| EPCC   	| intel   	|        32 	|               4 	| 38.53717971 	| 51.89793376 	|

#### EPCC - ICX

Training with and without intel optimized python & Tensorflow Ice Lake architecture. Only one node was available for these runs.

##### Training
| index  | system | num_ranks | total_time         | first_epoch_time  | second_epoch_time  | first_epoch_train_time | second_epoch_train_time | first_epoch_test_time | second_epoch_test_time | imgs_per_s_second_epoch | imgs_per_s_first_epoch | train_accuracy     | test_accuracy      | train_loss          | test_loss           | batch_size | epochs | learning_rate | no_cache |
|--------|--------|-----------|--------------------|-------------------|--------------------|------------------------|-------------------------|-----------------------|------------------------|-------------------------|------------------------|--------------------|--------------------|---------------------|---------------------|------------|--------|---------------|----------|
| run_j1 | ICX    | 1         | 150662.70891571045 | 4983.639632463455 | 5049.243052482605  | 4761.912266016007      | 4831.074041366577       | 221.72523140907288    | 218.16710019111636     | 4.015670187185183       | 4.073993579942782      | 0.8532552123069763 | 0.852003812789917  | 0.21356502175331116 | 0.2126753032207489  | 32         | 30     | 0.001         | True     |
| run_j2 | ICX    | 2         | 103711.89777755736 | 5459.10152053833  | 3850.113874197006  | 5201.835367918015      | 3688.9679811000815      | 257.2456078529358     | 161.12971186637878     | 5.258923389791732       | 3.729452900345184      | 0.8568906188011169 | 0.8335456848144531 | 0.20529469847679138 | 0.2204301804304123  | 32         | 30     | 0.001         | True     |
| run_j4 | ICX    | 4         | 81546.39018201828  | 2759.53519654274  | 2768.5064277648926 | 2638.023328065872      | 2650.5064244270325      | 121.50969576835632    | 117.99768447875977     | 7.319355962019127       | 7.35399107111898       | 0.8437639474868774 | 0.8561383485794067 | 0.22493310272693634 | 0.20200051367282867 | 32         | 30     | 0.001         | True     |

##### Inference

| index  | num_ranks | total              | imgs_per_s         |
|--------|-----------|--------------------|--------------------|
| run_j1 | 1         | 912.7746522426604  | 2.1911213190309997 |
| run_j2 | 2         | 497.28040766716    | 4.021875724769437  |
| run_j4 | 4         | 310.29732847213745 | 6.445430935057458  |
