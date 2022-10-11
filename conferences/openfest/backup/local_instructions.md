## Local execution of exercises

If there's an issue with mybinder, the whole Workshop can be executed locally on linux or mac.

**Open a terminal:**

0. Make sure you have python installed:
```
python -V
```
It's very much recommended to use a new virutal environment. Conda is a great way to manage those:
https://conda.io/projects/conda/en/latest/user-guide/install/index.html

1. Clone the repo:
```
git clone https://github.com/versatile-data-kit-amld/linear-regression-example-unsolved.git
cd linear-regression-example-unsolved
```

2. Install Jupyter Lab if you have not done so already:
```
pip install jupyterlab
```

3. Install VDK  and dependencies (make sure you are in the cloned repo directory):
```
pip install -r requirements.txt
```

4. Source environment variables:
```
source start
```

5. Start Jupyter:
```
jupyter lab
```

Navigate to the **setup.ipynb** file and continue with the exercises.
