
If there's an issue with mybinder the whole Workshop can be executed locally on linux or mac. 
For each workshop excersice: 


Open a terminal

0. Make sure you have python installed 
```
python -V
```
It's very much recommended to use new virutal environment. Conda is great way to manage those: 
https://conda.io/projects/conda/en/latest/user-guide/install/index.html

1. Clone repo
```
git clone https://github.com/versatile-data-kit-amld/linear-regression-example-unsolved.git
cd linear-regression-example-unsolved
```


2. Install jupyterlab if you have not install it already 

```
pip install jupyterlab
```

3. Install VDK  and dependencies (make sure you are in the clone repo directory): 

```
pip install -r requirements.txt
```

4. Source environment variables
```
source start
```

5. Start jupyter 
```
jupyter lab
```

Navigate to setup.ipynb file and continue with the excersize. 
