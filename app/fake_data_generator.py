import numpy as np
import pandas as pd
import random

np.random.seed(42)
random.seed(42)

def fake_data():
    sped = 109623 / 883264
    ell = 109809 / 883264
    frl = .402
    asian = 28214/886517
    black = 40229/886517
    hispanic = 306215/886517
    white = 460186/886517
    other = 1 - (asian + black + hispanic + white)
    race_probs = [asian, black, hispanic, white, other]
    students = 500000
    
    # Generate random data based on proportions
    sped_flags = np.random.choice([0, 1], size=students, p=[1-sped, sped])
    frl_flags = np.random.choice([0, 1], size=students, p=[1-frl, frl])
    ell_flags = np.random.choice([0, 1], size=students, p=[1-ell, ell])
    race_flags = np.random.choice(range(5), size=students, p=race_probs)  # choose from 4 categories

    # Create individual race flags
    asian_flags = [1 if race == 0 else 0 for race in race_flags]
    black_flags = [1 if race == 1 else 0 for race in race_flags]
    hispanic_flags = [1 if race == 2 else 0 for race in race_flags]
    white_flags = [1 if race == 3 else 0 for race in race_flags]
    other_flags = [1 if race == 4 else 0 for race in race_flags]
    
    # Create the DataFrame
    student_ids = np.arange(1, students+1)
    num_schools = 176

    # Define mappings for flag combinations and GPAs
    gpa_mapping = {
        (0, 0, 0, 0, 0, 0, 0): {'starting_gpa': .7, 'ending_gpa': .75},
        (1, 0, 0, 0, 0, 0, 0): {'starting_gpa': .4, 'ending_gpa': .4},
        (0, 1, 0, 0, 0, 0, 0): {'starting_gpa': .55, 'ending_gpa': .57},
        (0, 0, 1, 0, 0, 0, 0): {'starting_gpa': .6, 'ending_gpa': .63},
        (1, 1, 0, 0, 0, 0, 0): {'starting_gpa': .6, 'ending_gpa': .61},
        (1, 0, 1, 0, 0, 0, 0): {'starting_gpa': .3, 'ending_gpa': .32},
        (0, 1, 1, 0, 0, 0, 0): {'starting_gpa': .45, 'ending_gpa': .5},
        (1, 1, 1, 0, 0, 0, 0): {'starting_gpa': .5, 'ending_gpa': .51},
        (0, 0, 0, 1, 0, 0, 0): {'starting_gpa': .62, 'ending_gpa': .65},
        (1, 0, 0, 1, 0, 0, 0): {'starting_gpa': .43, 'ending_gpa': .46},
        (0, 1, 0, 1, 0, 0, 0): {'starting_gpa': .51, 'ending_gpa': .53},
        (0, 0, 1, 1, 0, 0, 0): {'starting_gpa': .63, 'ending_gpa': .67},
        (1, 1, 0, 1, 0, 0, 0): {'starting_gpa': .68, 'ending_gpa': .72},
        (1, 0, 1, 1, 0, 0, 0): {'starting_gpa': .54, 'ending_gpa': .58},
        (0, 1, 1, 1, 0, 0, 0): {'starting_gpa': .58, 'ending_gpa': .62},
        (1, 1, 1, 1, 0, 0, 0): {'starting_gpa': .63, 'ending_gpa': .66},
        (0, 0, 0, 0, 1, 0, 0): {'starting_gpa': .45, 'ending_gpa': .55},
        (1, 0, 0, 0, 1, 0, 0): {'starting_gpa': .32, 'ending_gpa': .35},
        (0, 1, 0, 0, 1, 0, 0): {'starting_gpa': .4, 'ending_gpa': .43},
        (0, 0, 1, 0, 1, 0, 0): {'starting_gpa': .47, 'ending_gpa': .52},
        (1, 1, 0, 0, 1, 0, 0): {'starting_gpa': .3, 'ending_gpa': .35},
        (1, 0, 1, 0, 1, 0, 0): {'starting_gpa': .35, 'ending_gpa': .4},
        (0, 1, 1, 0, 1, 0, 0): {'starting_gpa': .37, 'ending_gpa': .4},
        (1, 1, 1, 0, 1, 0, 0): {'starting_gpa': .25, 'ending_gpa': .27},
        (0, 0, 0, 0, 0, 1, 0): {'starting_gpa': .2, 'ending_gpa': .21},
        (1, 0, 0, 0, 0, 1, 0): {'starting_gpa': .22, 'ending_gpa': .24},
        (0, 1, 0, 0, 0, 1, 0): {'starting_gpa': .23, 'ending_gpa': .28},
        (0, 0, 1, 0, 0, 1, 0): {'starting_gpa': .1, 'ending_gpa': .15},
        (1, 1, 0, 0, 0, 1, 0): {'starting_gpa': .2, 'ending_gpa': .18},
        (1, 0, 1, 0, 0, 1, 0): {'starting_gpa': .24, 'ending_gpa': .26},
        (0, 1, 1, 0, 0, 1, 0): {'starting_gpa': .27, 'ending_gpa': .32},
        (1, 1, 1, 0, 0, 1, 0): {'starting_gpa': .34, 'ending_gpa': .31},
        (0, 0, 0, 0, 0, 0, 1): {'starting_gpa': .3, 'ending_gpa': .32},
        (1, 0, 0, 0, 0, 0, 1): {'starting_gpa': .4, 'ending_gpa': .41},
        (0, 1, 0, 0, 0, 0, 1): {'starting_gpa': .25, 'ending_gpa': .34},
        (0, 0, 1, 0, 0, 0, 1): {'starting_gpa': .27, 'ending_gpa': .33},
        (1, 1, 0, 0, 0, 0, 1): {'starting_gpa': .17, 'ending_gpa': .24},
        (1, 0, 1, 0, 0, 0, 1): {'starting_gpa': .19, 'ending_gpa': .27},
        (0, 1, 1, 0, 0, 0, 1): {'starting_gpa': .24, 'ending_gpa': .3},
        (1, 1, 1, 0, 0, 0, 1): {'starting_gpa': .32, 'ending_gpa': .4},
    }

    # Create the DataFrame
    df = pd.DataFrame({
        'student_id': student_ids,
        'sped_flag': sped_flags,
        'frl_flag': frl_flags,
        'ell_flag': ell_flags,
        'asian_flag': asian_flags,
        'black_flag': black_flags,
        'hispanic_flag': hispanic_flags,
        'white_flag': white_flags,
        'school_id': np.random.randint(1, num_schools + 1, size=students)
    })
    
    # Create a set of unique keys present in your dataframe
    unique_combinations = set(zip(df['school_id'], df['sped_flag'], df['frl_flag'], df['ell_flag'], df['asian_flag'], df['black_flag'], df['hispanic_flag'], df['white_flag']))

    # Now, only generate adjustments for these combinations
    school_adjustments = {combination: np.random.uniform(low=-0.1, high=0.1) 
                      for combination in unique_combinations}
    
    # Only look up GPAs for existing combinations
    df['starting_gpa'] = [gpa_mapping[combination]['starting_gpa'] if combination in gpa_mapping else np.nan for combination in zip(
        df['sped_flag'], df['frl_flag'], df['ell_flag'], df['asian_flag'], df['black_flag'], df['hispanic_flag'], df['white_flag'])]
    df['ending_gpa'] = [gpa_mapping[combination]['ending_gpa'] if combination in gpa_mapping else np.nan for combination in zip(
        df['sped_flag'], df['frl_flag'], df['ell_flag'], df['asian_flag'], df['black_flag'], df['hispanic_flag'], df['white_flag'])]
    
    # Apply the adjustment values to each row based on school_id and flag combination
    df['adjustment_value'] = [school_adjustments[combination] for combination in zip(
        df['school_id'], df['sped_flag'], df['frl_flag'], df['ell_flag'], df['asian_flag'], df['black_flag'], df['hispanic_flag'], df['white_flag'])]

    # Calculate adjusted GPA
    df['gpa_adjusted'] = df['ending_gpa'] + df['adjustment_value']
    df['gpa'] = df['gpa_adjusted'].apply(lambda x: 1 if x > 1 else 0 if x < 0 else x)
    
    # Create a new DataFrame with the desired columns
    df_keep = df[['student_id', 'school_id', 'sped_flag', 'frl_flag', 'ell_flag', 'asian_flag', 'black_flag', 
                  'hispanic_flag', 'white_flag', 'starting_gpa', 'gpa']].copy()
    
    df_keep.to_csv('fake_data.csv')
    
    return df_keep