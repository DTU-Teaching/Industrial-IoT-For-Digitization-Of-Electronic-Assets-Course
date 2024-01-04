# Data Driven Modelling and System Identification. 

In today's afternoon session, our focus will be on learning how to identify a system purely from measured data.
To make things more interesting, each group will write down an ARX model they like the most.
Please, consider a reasonable 5 as the maximum number of lags for y(t) and u(t). Eventually, you can also introduce some delay between the inputs and the outputs. 
Furthermore, the model should be Single Input Single Output (SISO), and linear.

As soon you have created your ARX model (**example:** $y_t = a_1 y_{t-1} + a_2 y_{t-2} + b_1 u_{t-1}+ \mathcal{N}(0,0.1))$, send it at alqua@dtu.dk

**NOTE**: Keep your ARX model secret from other groups.


### Setup the Environment and Requirements Installation
Before we start, please check if you are familiar with creating a conda environment and installing the requirements from the .txt file. Moreover, ensure you can use the conda environment created as a kernel in Visual Studio Code. 

Open your terminal and run the following command:

```bash
#create a new conda environment
conda create -n module3_env python=3.11
#activate your environment 
conda activate module3_env
# install jupyter extension
conda install jupyter
# install ipykernel extension
conda install ipykernel
# install pip extension
conda install pip
# Finally, install the libraries needed for this module
pip install -r requirements.txt
```
If the installation fails for some package, please remove it from the requirements.txt file and check the documentation online for an alternative installation.

### Preparation
In order to create the SISO data you can follow the instructions given in the morning session. 
Create a function that generates random data and returns a train and test set. 
You can follow the the steps below: 

- Create a python function named ```generate_siso_data(*args)```.
- Set the seed in numpy for reproducibility.
- Create a random integer signal sequence in numpy of size n, with $200\leq \boldsymbol{n} \leq 2000$.
- Create a zeros output vector in numpy.
- Introduce white noise in the output signal, i.e. $\mathcal{N} \sim (0,\sigma^2)$, where $0 \leq \boldsymbol{\sigma^2} \leq 0.7$
- Create a test dataset, with a size al least equal to 20% of the full dataset.


The function's structure should be as follows:

```python
def generate_siso_data(n, test_size, noise_level):
    """
    Generates synthetic Single Input Single Output (SISO) data for an ARX model with na=2 and nb=2.
    :param n: Number of data points to generate.
    :param test_size: Proportion of the dataset to include in the test split.
    :param noise_level: Standard deviation of the noise.
    :return: Tuple of (y_train, x_train, y_test, x_test), where y is the target series and x is the exogenous series.
    """

    # set the seed in numpy
    np.random.seed(...)

    # Generating exogenous input (x) as a random signal
    u = #generate the exogenous inputs of size n, you can use np.random.randint()
    y = #generate a zero vector of size n
    
    for t in range(n):

        # y(t) = a_1 y(t-1) + b1 y(t-1) + noise

    # Split the data into train and test.
    return y_train, u_train, y_test, u_test
```

Once you have generated the data, ensure the correctness with some visualization and save it as a .csv file, specifying the input and output variables in the file's header. 
The dataframe should contain two columns named $\textbf{y}$ and $\textbf{u}$.
As soon as your dataset is ready and tested, you can mail it to another group following this schema:

- $\textbf{Group 1}$ $\xrightarrow[\text{}]{to}$ $\textbf{Group 2}$

- $\textbf{Group 2}$ $\xrightarrow[\text{}]{to}$ $\textbf{Group 3}$

- $\textbf{Group 3}$ $\xrightarrow[\text{}]{to}$ $\textbf{Group 1}$

As soon as each group has received the **.csv** file, you can start modelling the data 

### Identify the ARX model from the data. 

Open the .csv file using pandas and create some simple (but nice and clear!) visualizations to understand the behavior of the system using one of the plotting libraries of your choice between [matplotlib](https://matplotlib.org/stable/), [plotly](https://plotly.com/python/), or [plotly-resampler](https://github.com/predict-idlab/plotly-resampler). 

FYI: In combination with Matplotlib, you can use [SciencePlots](https://github.com/garrettj403/SciencePlots), a style for scientific papers or presentations.


#### Build your Model
Let's get started with system identification. You are allowed to use any library you choose, although most examples are based on [SysIdentPy](https://sysidentpy.org/). This library provides a comprehensive extension to dynamic modeling, from linear models to neural networks. 
Please explore the [tutorials](https://sysidentpy.org/examples/basic_steps/) to develop some confidence and learn the basic methods of the library.


```python
# start by setting the degree of the polynomial
basis_function = Polynomial(degree=1)

#Build the model using Forward Regression Orthogonal Least Squares (FROLS)

model = FROLS(...)
    
    #set and test some of the parameters available such as 
    # order_selection, n_info_values, ylag, xlag, info_criteria
    # set the info_criteria = "aic" or "bic"
    # set estimator="least_squares"
    # set basis function = basis_function, using the one you have defined before. 
```

#### Fit your model
Now that you have defined the type of model, the complexity (order or lags) and some of the other parameters, fit your model using the train data. 

```python
model.fit(X=x_train, y=y_train) #please check the shape of your inputs
```
#### Predict using the Fitted Model.

```python
yhat = model.predict(X=x_test, y=y_test) #please check the shape of you inputs
```

#### Evaluate the prediction 
Now, evaluate predictions on the test dataframe. 
There are at least two important steps you have to follow:

##### 1. Check the performance indicators for a regression model.
```python
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sysidentpy.metrics import root_relative_squared_error

#you can use sklearn.metrics to compute mae, mse and rmse.
mae  = ...
mse  = ...
rmse = ...
#you can use sysidentpy.metrics to compute (root_relative_squared_error) rrse.
rrse = ...
```
##### 2. Check, Plot and Test the Residual of your predictions.
In today's lesson, we defined the residuals as the portion of the validation data not explained by the model and assumed the so-called *whiteness condition*, which states that the model's error follows a normal distribution $\epsilon(t) \sim \mathcal{N}(0,\sigma^2) $, with:
$\epsilon_t = y_t - \hat{y}_t$

##### 2.1 Use an histogram to plot the residuals of your model. Can you quantify the $\sigma^2$.
```python
import matplotlib.pyplot as plt

residuals = your_data - yhat

# Plotting the histogram of residuals
plt.hist(residuals, bins=20, edgecolor='black')
plt.xlabel('Residuals')
plt.ylabel('Frequency')
plt.title('Histogram of Residuals')
plt.show()
```

##### 3. Do they follow a normal distribution? Perform the Shapiro-Wilk test for normality on the residuals. 
```python
import scipy.stats as stats

shapiro_test = stats.shapiro(residuals_of_your_model)

print(f"Shapiro-Wilk Test Statistic: {shapiro_test[0]}, P-value: {shapiro_test[1]}")

# Interpretation
alpha = 0.05
if shapiro_test[1] < alpha:
    print("The residuals do not follow a normal distribution (reject H0)")
else:
    print("The residuals follow a normal distribution (fail to reject H0)")

```

##### 4. Check the autocorrelation and the cross-correlation  

```python
#Check the styles you have available in your matplotlib. 
plt.style.available
```

```python
# If seaborn-v0_8-notebook style is not available, 
# pick a random style from the ones available in yout matplotlib

ee = compute_residues_autocorrelation(y_test, yhat)
#========================
#Plot the residuals correlation or autocorrelation.
plot_residues_correlation(data=ee, title="Residuals Autocorrelation",
                          ylabel="$e^2$", 
                          style='seaborn-v0_8-notebook')
#========================
#Plot the cross-correlation of the residuals. 
x1e = compute_cross_correlation(y_test, yhat, x_test)

plot_residues_correlation(data=x1e, title="Residuals Cross-Correlations", 
                          ylabel="$x_1e$", 
                          style='seaborn-v0_8-notebook')
```
For more information, please check: 

- [Shapiro–Wilk test](https://en.wikipedia.org/wiki/Shapiro%E2%80%93Wilk_test)
- [Residual Analysis with Autocorrelation](https://se.mathworks.com/help/signal/ug/residual-analysis-with-autocorrelation.html)


##### When a model is a good model...

Ideally, a good model shows the following characteristics:
1. Low inference error metrics (mae, mse, rmse, rrse).
2. Residuals behaving like white noise, with no clear pattern.
3. The residual are not autocorrelated. 

###### Is your model not good enough?
Retrain the model using more lags and change some training parameters. 

###### Is your model ok?
If your model ok, store the coefficients of your final model in one dataframe, following this procedure: 

```python
r = pd.DataFrame(
    results(
        model.final_model,
        model.theta,
        model.err,
        model.n_terms,
        err_precision=8,
        dtype="sci",
    ),
    columns=["Regressors", "Parameters", "ERR"],
)
print(r)
```

And prepare one page .ppt (one per group) with all the relevant plots, parameters and results to be presented by one member of the group in 3 mins. 
 
**Optional:** Restart the system identification process using the same dataset, this time building a neural network to learn the input-output model. You can follow this [guide](https://sysidentpy.org/examples/narx_neural_network/) or the exercise on heatsink temperature forecast used during the lecture. 
