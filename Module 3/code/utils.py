import numpy as np 
from sklearn.model_selection import train_test_split



def generate_siso_data(n, test_size=0.2, noise_level=0.1, a1=0.5, a2=-0.3, b1=0.7, b2=-0.2):
    """
    Generates synthetic Single Input Single Output (SISO) data for an ARX model with na=2 and nb=2.
    :param n: Number of data points to generate.
    :param test_size: Proportion of the dataset to include in the test split.
    :param noise_level: Standard deviation of the noise.
    :param a1, a2: Coefficients for the autoregressive part of the model.
    :param b1, b2: Coefficients for the exogenous input part of the model.
    :return: Tuple of (y_train, x_train, y_test, x_test), where y is the target series and x is the exogenous series.
    """
    # Generating exogenous input (x) as a random signal
    u = np.random.randint(0, 2, size=n)

    # Generating the target series (y)
    y = np.zeros(n)
    for t in range(n):
        y[t] = a1 * y[t-1] + a2 * y[t-2] +  b1 * u[t-1] + b2 * u[t-2] + np.random.normal(0, noise_level)

    # Splitting the data into training and testing sets
    y_train, y_test, u_train, u_test = train_test_split(y, u, test_size=test_size, shuffle=False)

    return y_train, u_train, y_test, u_test