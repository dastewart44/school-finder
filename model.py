from sklearn.linear_model import LinearRegression

def calculate_school_estimates(df, student_characteristics):
    schools = df['school_id'].unique()
    estimated_gpas = {}

    for school in schools:
        # Create a model for the specific school
        school_df = df[df['school_id'] == school]
        
        # Your predictor variables here
        X = school_df[['sped_flag', 'frl_flag', 'ell_flag', 'asian_flag', 'black_flag', 'hispanic_flag', 'white_flag', 'starting_gpa']]
        y = school_df['gpa']
        
        model = LinearRegression().fit(X, y)
        
        # Predict the GPA for the given student's characteristics at this school
        predicted_gpa = model.predict(student_characteristics)
        estimated_gpas[school] = predicted_gpa[0]

    # Sort the estimated GPAs and get the top 5 schools
    sorted_results = sorted(estimated_gpas.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return sorted_results