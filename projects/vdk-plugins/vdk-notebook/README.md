# vdk-notebook

A new VDK plugin which supports running data jobs which consists of .ipynb files.
You can see [VDK Jupyter Integration VEP](https://github.com/vmware/versatile-data-kit/blob/main/specs/vep-994-jupyter-notebook-integration/README.md) for more information.


## Usage
To install the plugin you need to run:
```
pip install vdk-notebook
```

### Configuration
No specific notebook configurations are needed currently.

### Example
Here is a directory structure which consist of one parent directory "parent-dir" and two subdirectories.
One of the subdirectories is a data job("example-job"). This is how the structure looks like:
```
parent-dir
└── example-job
    ├── notebook.ipynb
    ├── requirements.txt
    └── config.ini
└── some-other-dir
```
To run the data job from the parent-dir we need to use:

```
vdk run example-job
```


### Testing
Testing this plugin locally requires installing the dependencies listed in vdk-plugins/vdk-notebook/requirements.txt

Run
```
pip install -r requirements.txt
```

## Architecture
See the architecture of the plugin in the "Detailed design" section of [the VEP](https://github.com/vmware/versatile-data-kit/blob/main/specs/vep-994-jupyter-notebook-integration/README.md).
