
import pandas as pd
from sklearn.model_selection import train_test_split

def filter_rsos_by_min_state_count(df, state_threshold):
    '''get lists of rsos that meet and do not meet the threshold'''
    rso2count = df['NUMBER'].value_counts()
    rsos_geq_threshold = rso2count[rso2count.values >= state_threshold].index
    rsos_l_threshold = rso2count[rso2count.values < state_threshold].index
    return list(rsos_geq_threshold), list(rsos_l_threshold)
    
    
def rso_train_test_split(df, rsos_meet_threshold):
    '''given a list of RSOs split them into train and test dfs; including their tyeps'''
    # create DF to split
    df_object_type = df[df['NUMBER'].isin(rsos_meet_threshold)].drop_duplicates(subset='NUMBER')[['NUMBER', 'TYPE']].reset_index(drop=True)
    X_train, X_test, y_train, y_test = train_test_split(df_object_type['NUMBER'], df_object_type['TYPE'], test_size=0.2, random_state=209, stratify=df_object_type['TYPE'] )

    df_objects_train = pd.DataFrame({'NUMBER': X_train,'TYPE': y_train}).reset_index(drop=True)
    df_objects_test = pd.DataFrame({'NUMBER': X_test,'TYPE': y_test}).reset_index(drop=True)
    
    return df_objects_train, df_objects_test

def keep_N_rows_per_number(df, n_states):
    '''keeps exactly n states per object'''
    result = []
    for number in df['NUMBER'].unique():
        number_rows = df[df['NUMBER'] == number].head(n_states)
        result.append(number_rows)
    
    return pd.concat(result)

def assemble_state_df(df, rso_list,  state_threshold):
    '''reduce df to rsos in a list and with only states in threshold'''
    return keep_N_rows_per_number(df[df['NUMBER'].isin(rso_list)], state_threshold).reset_index(drop=True)

def assemble_scaled_state_df(df, rso_list, features_to_scale,  state_threshold, scaler, fit_scaler=False):
    '''scale the DF and reassemble'''
    df_states = assemble_state_df(df, rso_list, state_threshold)
    if fit_scaler:
        X_scaled = scaler.fit_transform(df_states[features_to_scale])
    else:
        X_scaled = scaler.transform(df_states[features_to_scale])
        
    X_scaled = pd.DataFrame(X_scaled, columns=features_to_scale)
    return pd.concat([df_states['NUMBER'].reset_index(drop=True),df_states['TYPE'].reset_index(drop=True), X_scaled, ], axis=1), scaler


