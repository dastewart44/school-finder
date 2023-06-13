from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import numpy as np
import pickle

def model(df):
    schools = df['school_id'].unique()
    
    rf_count = 0
    lin_count = 0
    
    for school in schools:
        school_df = df[df['school_id'] == school]
        X = school_df[['sped_flag', 'frl_flag', 'ell_flag', 'asian_flag', 'black_flag', 'hispanic_flag', 'white_flag', 'starting_gpa']]
        y = school_df['gpa']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model_linear = LinearRegression().fit(X_train, y_train)
        model_rf = RandomForestRegressor().fit(X_train, y_train)

        # Evaluate models
        y_pred_linear = model_linear.predict(X_test)
        y_pred_rf = model_rf.predict(X_test)

        mse_linear = mean_squared_error(y_test, y_pred_linear)
        mse_rf = mean_squared_error(y_test, y_pred_rf)
        
        if np.mean(mse_rf) < np.mean(mse_linear):  
            pkl_filename = f'models/{school}_model.pkl'
            with open(pkl_filename, 'wb') as file:
                pickle.dump(model_rf, file)
            rf_count += 1
        else :
            pkl_filename = f'models/{school}_model.pkl'
            with open(pkl_filename, 'wb') as file:
                pickle.dump(model_linear, file)
            lin_count += 1
      
    return rf_count, lin_count
        
