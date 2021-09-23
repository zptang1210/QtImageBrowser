Deploy on your server:
1. change gypsum.json to your configuration
2. git clone the repo and put it to the processor_path on your server
3. create tmp/scripts folder on your processor_path
4. write your own template_path

Run on your local machine:
1. follow the following commands to create a conda environment
    * conda create -n your_env_name python=3.8
    * conda activate your_env_name
    * pip install PyQt5
    * pip install numpy
    * pip install Pillow
    * pip install opencv-python
    * pip install opencv-contrib-python
    * pip install decord
    * pip install pexpect
2. To run the program, follow the following commands
    * conda activate your_env_name
    * go to the main folder
    * python ImageBrowser.py