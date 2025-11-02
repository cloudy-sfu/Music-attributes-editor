# Music attributes editor

Edit audio files' title, album, artists in batch in Windows

![](https://shields.io/badge/dependencies-Python_3.12-blue)
![](https://shields.io/badge/OS-Windows_10_64--bit-navy)



## Install

### From release

Download the latest release, unzip, and run `Music attributes renamer.exe`.



### From source code

Create a Python virtual environment and run the following command.

```
pip install -r requirements.txt
```

To generate `app.spec`, run the following command. This file is manually modified after generated.

```
pyi-makespec app.py
```

To compile from source code, run the following command.

```
pyinstaller app.spec
```



## Usage



1. Select the local folder which is the album.
2. Click "Load". It will display all audio files in the selected folder and its subfolders.
3. Edit music meta data.
4. Click "Submit". If meta data still cannot display in operation system's file explorer, click "unblock" for corresponding to these audio files and submit again.



