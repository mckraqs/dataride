# Introduction

Hi! It's great you chose to build your pipelines with `mage-ai`. Please look at the below instructions so you can make use of it fully.

# How to set up mage-ai environment

There are several methods to start using mage-ai. Below you can find list of 2 easiest approaches:

- **run default image**:
  - folks at Mage maintain Docker image at Dockerhub that is available to download and run. Simply execute the below command:
  - ```docker run -it -p 6789:6789 -v $(pwd):/home/src mageai/mageai mage start dataride_mage_pipelines```
- **install package**:
  - on the other hand, you can install package via pip or conda and start the engine. Follow two below commands
  - `pip install mage-ai` (for pip) / `conda install -c conda-forge mage-ai` (for conda)
  - `mage start dataride_mage_pipelines` and access the environment at `http://localhost:6789`

# For more information

If this document isn't enough, please refer to [mage-ai Github repository](https://github.com/mage-ai/mage-ai). It contains thorough documentation and it's likely that it will answer your questions!