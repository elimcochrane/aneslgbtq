import pandas as pd
import numpy as np
from samplics.estimation import TaylorEstimator
from samplics.utils.types import PopParam

def load_and_prepare_data(csv_file_path, var_dict):
    column_mapping = var_dict
    df = pd.read_csv(csv_file_path)
    existing_cols = {old: new for old, new in column_mapping.items() if old in df.columns}
    df_renamed = df.rename(columns=existing_cols)
    return df_renamed, column_mapping

def basic_descriptive_stats(df, theme_dict):
    trans_questions = list(theme_dict['trans_qs'])
    gay_questions = list(theme_dict['gay_qs'])
    
    trans_cols = [col for col in trans_questions if col in df.columns]
    gay_cols = [col for col in gay_questions if col in df.columns]
    demo_cols = [col for col in df.columns if col.startswith('resp_')]

    for group_name, cols in [("Transgender Questions", trans_cols), 
                             ("Gay/LGB Questions", gay_cols), 
                             ("Demographics", demo_cols)]:
        if cols:
            for col in cols:
                valid_count = df[col].notna().sum()
                missing_count = df[col].isna().sum()
    return trans_cols, gay_cols, demo_cols

def samplics_analysis(df): # using samplics taylorestimator + fallback
    weights = df['weight'] if 'weight' in df.columns else pd.Series(1.0, index=df.index)

    analysis_vars = []
    for col in df.columns:
        if col in ['weight', 'case_id', 'int_mode', 'prepost_status', 'sample_type', 'psu', 'stratum', 'sample_mode']:
            continue
        if df[col].dtype in ['object', 'string']:
            continue
        analysis_vars.append(col)
    
    results = {}

    for var in analysis_vars:
        valid_mask = df[var].notna() & weights.notna()
        if valid_mask.sum() <= 10:
            continue
        
        try:
            if not pd.api.types.is_numeric_dtype(df[var]):
                continue
                
            if "therm" in var:
                therm_mask = valid_mask & (df[var] >= 0) & (df[var] <= 100)
                if therm_mask.sum() <= 10:
                    continue
                    
                taylor_est = TaylorEstimator(PopParam.mean)
                mean_est = taylor_est.estimate(
                    y=df.loc[therm_mask, var].astype(float),
                    samp_weight=weights.loc[therm_mask].astype(float),
                    remove_nan=True
                )
                
                if mean_est is not None and hasattr(mean_est, 'point_est'):
                    results[var] = {
                        "type": "continuous",
                        "mean": float(mean_est.point_est),
                        "se": float(mean_est.stderror) if hasattr(mean_est, 'stderror') else None,
                        "n": int(therm_mask.sum())
                    }
                else:
                    pass
                    
            else:
                categories = df.loc[valid_mask, var].dropna().unique()
                numeric_categories = []
                for cat in categories:
                    try:
                        float(cat)
                        numeric_categories.append(cat)
                    except (ValueError, TypeError):
                        continue
                
                if len(numeric_categories) == 0:
                    continue
                    
                cat_results = {}
                for cat in numeric_categories:
                    cat_mask = valid_mask & (df[var] == cat)
                    if cat_mask.sum() < 5:
                        continue
                        
                    y_binary = cat_mask.astype(int)
                    taylor_est = TaylorEstimator(PopParam.ratio)
                    prop_est = taylor_est.estimate(
                        y=y_binary.astype(float),
                        samp_weight=weights.astype(float),
                        remove_nan=True
                    )
                    
                    if prop_est is not None and hasattr(prop_est, 'point_est'):
                        cat_results[float(cat)] = {
                            "proportion": float(prop_est.point_est),
                            "se": float(prop_est.stderror) if hasattr(prop_est, 'stderror') else None
                        }
                
                if cat_results:
                    results[var] = {
                        "type": "categorical",
                        "categories": cat_results,
                        "n": int(valid_mask.sum())
                    }
                    
        except Exception as e:
            try:
                if "therm" in var:
                    therm_data = df.loc[valid_mask & (df[var] >= 0) & (df[var] <= 100), var]
                    if len(therm_data) > 0:
                        results[var] = {
                            "type": "continuous",
                            "mean": float(therm_data.mean()),
                            "se": None,
                            "n": len(therm_data),
                            "fallback": True
                        }
                else:
                    value_counts = df.loc[valid_mask, var].value_counts()
                    if len(value_counts) > 0:
                        results[var] = {
                            "type": "categorical", 
                            "categories": {float(k): {"proportion": v/len(df.loc[valid_mask, var]), "se": None} 
                                         for k, v in value_counts.items() if pd.api.types.is_numeric_dtype(type(k))},
                            "n": int(valid_mask.sum()),
                            "fallback": True
                        }
            except:
                pass

    return results

def calculate_weighted_mean(series, weights):
    valid_mask = series.notna() & weights.notna()
    if valid_mask.sum() == 0:
        return np.nan
    return np.average(series[valid_mask], weights=weights[valid_mask])

def calculate_weighted_std(series, weights):
    valid_mask = series.notna() & weights.notna()
    if valid_mask.sum() <= 1:
        return np.nan
    
    weighted_mean = calculate_weighted_mean(series, weights)
    variance = np.average((series[valid_mask] - weighted_mean)**2, weights=weights[valid_mask])
    return np.sqrt(variance)