# Music attributes renamer
Rename music attributes in Windows

![](https://shields.io/badge/dependencies-Python_3.12-blue)
![](https://shields.io/badge/OS-Windows_10_64--bit-navy)



## Install

Download the latest release, unzip, and run `Music_attributes_renamer.exe`.

**Developers**:

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
2. Click "Load".
3. Modify music meta data.
4. Click "Submit".

![image-20241130045902150](./assets/image-20241130045902150.png)
