# Tutorial

## Pre-processing

The preprocessing component of the pipeline consists of two stages, extraction and HDF conversion. 

 - The extraction step unzips the raw data from the CEDA archive. 
 - The HDF conversion converts the raw data files into a stand alone HDF file. 
   - This collects all of the brightness temperature channels, radiance channels, and product masks into a single file. 
   - This step is neccesary to cut down the number of I/O calls during training.
   - This step also converts the radiance channels to reflectance.

## Training

## Post-processing
