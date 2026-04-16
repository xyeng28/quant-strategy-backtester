import numpy as np
from sklearn.linear_model import LinearRegression

def linear_regression(df: pd.DataFrame, y_col:str, x_cols:list) -> tuple[float, np.ndarray]:
    """
    r squared = 1 -> perfect fit, explains all variability in y
    r squared = 0 -> explains none of the variability, same as just predicting the mean by using the average of (wheat) daily returns
    r squared < 0 -> model is worse than predicting the mean
    :param returns_df:
    :return:
    """
    y = df[y_col]
    X = df[x_cols]
    model = LinearRegression()
    model.fit(X, y)
    print(f'model coefficients: {model.coef_}')
    print(f'model intercept: {model.intercept_}')
    r_square = model.score(X, y)
    y_pred = model.predict(X)
    print(f'r square: {r_square}')
    print(f'predicted values: {y_pred}')
    return r_square, y_pred