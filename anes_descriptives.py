import pandas as pd
import numpy as np
import json
from datetime import datetime

def generate_descriptive_json(df, trans_cols=None, gay_cols=None, output_file=None):
    results = {
        "metadata": {
            "analysis_date": datetime.now().isoformat(),
            "total_respondents": len(df),
            "total_variables": len(df.columns)
        },
        "transgender_questions": {},
        "gay_lgb_questions": {},
        "demographics": {},
        "summary_statistics": {}
    }
    
    if trans_cols is None:
        trans_cols = [col for col in df.columns if 'trans' in col.lower()]
    if gay_cols is None:
        gay_cols = [col for col in df.columns if 'gay' in col.lower()]
    
    demo_cols = [col for col in df.columns if col.startswith('resp_')]
    other_cols = [col for col in df.columns if col not in trans_cols + gay_cols + demo_cols + ['weight', 'case_id'] and not col.startswith(('case_id', 'int_mode', 'prepost_status', 'sample_type', 'psu', 'stratum', 'sample_mode'))]
    
    results["transgender_questions"] = _analyze_question_group(df, trans_cols, "Transgender")
    results["gay_lgb_questions"] = _analyze_question_group(df, gay_cols, "Gay/LGB") 
    results["demographics"] = _analyze_question_group(df, demo_cols, "Demographics")
    results["other_variables"] = _analyze_question_group(df, other_cols, "Other")
    
    results["summary_statistics"] = _generate_summary_stats(df, trans_cols, gay_cols, demo_cols)
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    return results

def _analyze_question_group(df, columns, group_name):
    group_results = {
        "group_info": {
            "name": group_name,
            "total_questions": len(columns),
            "questions_with_data": 0
        },
        "questions": {}
    }
    
    weights = df['weight'] if 'weight' in df.columns else pd.Series(1.0, index=df.index)
    
    for col in columns:
        if col not in df.columns:
            continue
            
        valid_data = df[col].dropna()
        if len(valid_data) == 0:
            continue
        
        # skip non-numeric columns
        if df[col].dtype == 'object' or df[col].dtype == 'string':
            try:
                pd.to_numeric(df[col], errors='raise')
            except (ValueError, TypeError):
                continue
            
        group_results["group_info"]["questions_with_data"] += 1
        
        # define if therm or not
        is_thermometer = 'therm' in col.lower()
        
        question_stats = {
            "variable_name": col,
            "question_type": "thermometer" if is_thermometer else "categorical",
            "total_responses": len(valid_data),
            "missing_responses": int(df[col].isna().sum()),
            "response_rate": len(valid_data) / len(df) * 100
        }
        
        if is_thermometer:
            try:
                numeric_data = pd.to_numeric(valid_data, errors='coerce')
                valid_therm = numeric_data[(numeric_data >= 0) & (numeric_data <= 100)].dropna()
                
                if len(valid_therm) > 0:
                    question_stats.update({
                        "valid_thermometer_responses": len(valid_therm),
                        "mean": float(valid_therm.mean()),
                        "median": float(valid_therm.median()),
                        "std": float(valid_therm.std()),
                        "min": float(valid_therm.min()),
                        "max": float(valid_therm.max()),
                        "percentiles": {
                            "25th": float(valid_therm.quantile(0.25)),
                            "50th": float(valid_therm.quantile(0.50)),
                            "75th": float(valid_therm.quantile(0.75))
                        }
                    })
                    
                    if 'weight' in df.columns:
                        valid_mask = (pd.to_numeric(df[col], errors='coerce') >= 0) & \
                                   (pd.to_numeric(df[col], errors='coerce') <= 100) & \
                                   df[col].notna() & weights.notna()
                        if valid_mask.sum() > 0:
                            weighted_mean = np.average(
                                pd.to_numeric(df.loc[valid_mask, col], errors='coerce'), 
                                weights=weights[valid_mask]
                            )
                            question_stats["weighted_mean"] = float(weighted_mean)
                else:
                    question_stats.update({
                        "valid_thermometer_responses": 0,
                        "mean": None,
                        "median": None,
                        "std": None,
                        "min": None,
                        "max": None
                    })
            except Exception as e:
                question_stats["error"] = str(e)
        else:
            try:
                try:
                    numeric_data = pd.to_numeric(valid_data)
                except (ValueError, TypeError):
                    numeric_data = valid_data
                
                value_counts = numeric_data.value_counts().sort_index()
                
                filtered_counts = {}
                filtered_percentages = {}
                
                for value, count in value_counts.items():
                    try:
                        numeric_key = float(value) if pd.api.types.is_numeric_dtype(type(value)) else str(value)
                        if isinstance(numeric_key, (int, float)) and not np.isnan(numeric_key):
                            filtered_counts[int(numeric_key) if float(numeric_key).is_integer() else numeric_key] = int(count)
                            filtered_percentages[int(numeric_key) if float(numeric_key).is_integer() else numeric_key] = round(count / len(numeric_data) * 100, 2)
                    except (ValueError, TypeError):
                        continue
                
                if filtered_counts:
                    question_stats.update({
                        "unique_values": len(filtered_counts),
                        "value_counts": filtered_counts,
                        "percentages": filtered_percentages,
                        "mode": None
                    })
                    
                    try:
                        mode_val = numeric_data.mode()
                        if len(mode_val) > 0 and pd.api.types.is_numeric_dtype(type(mode_val.iloc[0])):
                            mode_numeric = float(mode_val.iloc[0])
                            question_stats["mode"] = int(mode_numeric) if mode_numeric.is_integer() else mode_numeric
                    except:
                        question_stats["mode"] = None
                    
                    if 'weight' in df.columns:
                        weighted_counts = {}
                        weighted_percentages = {}
                        valid_mask = df[col].notna() & weights.notna()
                        
                        if valid_mask.sum() > 0:
                            total_weight = weights[valid_mask].sum()
                            for value in filtered_counts.keys():
                                try:
                                    value_mask = valid_mask & (pd.to_numeric(df[col], errors='coerce') == value)
                                    if value_mask.sum() > 0:
                                        weighted_count = weights[value_mask].sum()
                                        weighted_counts[value] = float(weighted_count)
                                        weighted_percentages[value] = float(weighted_count / total_weight * 100)
                                except:
                                    continue
                            
                            if weighted_counts:
                                question_stats["weighted_counts"] = weighted_counts
                                question_stats["weighted_percentages"] = weighted_percentages
                else:
                    question_stats.update({
                        "unique_values": 0,
                        "value_counts": {},
                        "percentages": {},
                        "mode": None,
                        "error": "No numeric values found"
                    })
            except Exception as e:
                question_stats["error"] = str(e)
        
        group_results["questions"][col] = question_stats
    
    return group_results

def _generate_summary_stats(df, trans_cols, gay_cols, demo_cols):
    summary = {
        "data_quality": {
            "total_respondents": len(df),
            "completely_missing_cases": 0,
            "partially_complete_cases": 0,
            "complete_cases": 0
        },
        "question_group_summary": {
            "transgender": {
                "total_questions": len(trans_cols),
                "avg_response_rate": 0,
                "questions_with_high_missingness": 0
            },
            "gay_lgb": {
                "total_questions": len(gay_cols), 
                "avg_response_rate": 0,
                "questions_with_high_missingness": 0
            },
            "demographics": {
                "total_questions": len(demo_cols),
                "avg_response_rate": 0,
                "questions_with_high_missingness": 0
            }
        },
        "weights_info": {
            "has_weights": 'weight' in df.columns,
            "weight_statistics": {}
        }
    }
    
    all_survey_cols = trans_cols + gay_cols + demo_cols
    if all_survey_cols:
        missing_per_respondent = df[all_survey_cols].isna().sum(axis=1)
        summary["data_quality"]["completely_missing_cases"] = (missing_per_respondent == len(all_survey_cols)).sum()
        summary["data_quality"]["partially_complete_cases"] = ((missing_per_respondent > 0) & (missing_per_respondent < len(all_survey_cols))).sum()
        summary["data_quality"]["complete_cases"] = (missing_per_respondent == 0).sum()
    
    for group_name, cols in [("transgender", trans_cols), ("gay_lgb", gay_cols), ("demographics", demo_cols)]:
        if cols:
            group_cols = [col for col in cols if col in df.columns]
            if group_cols:
                response_rates = []
                high_missingness = 0
                
                for col in group_cols:
                    response_rate = (df[col].notna().sum() / len(df)) * 100
                    response_rates.append(response_rate)
                    if response_rate < 50:
                        high_missingness += 1
                
                summary["question_group_summary"][group_name]["avg_response_rate"] = round(np.mean(response_rates), 2)
                summary["question_group_summary"][group_name]["questions_with_high_missingness"] = high_missingness
    
    if 'weight' in df.columns:
        weights = df['weight'].dropna()
        summary["weights_info"]["weight_statistics"] = {
            "mean": float(weights.mean()),
            "median": float(weights.median()),
            "std": float(weights.std()),
            "min": float(weights.min()),
            "max": float(weights.max()),
            "total_weighted_n": float(weights.sum())
        }
    
    return summary

def save_descriptive_json(df, trans_cols=None, gay_cols=None, filename="anes_descriptive_stats.json"):
    return generate_descriptive_json(df, trans_cols, gay_cols, filename)

def print_summary_report(stats_dict): 
    print("Summary Report:")   
    # metadata
    metadata = stats_dict["metadata"]
    print(f"\nAnalysis Date: {metadata['analysis_date']}")
    print(f"Total Respondents: {metadata['total_respondents']:,}")
    print(f"Total Variables: {metadata['total_variables']}")
    
    # data quality
    quality = stats_dict["summary_statistics"]["data_quality"]
    print(f"\nData Quality:")
    print(f"  Complete cases: {quality['complete_cases']:,} ({quality['complete_cases']/metadata['total_respondents']*100:.1f}%)")
    print(f"  Partially complete: {quality['partially_complete_cases']:,} ({quality['partially_complete_cases']/metadata['total_respondents']*100:.1f}%)")
    print(f"  Completely missing: {quality['completely_missing_cases']:,} ({quality['completely_missing_cases']/metadata['total_respondents']*100:.1f}%)")
    
    # question groups
    print(f"\nQuestion Groups:")
    for group_name, group_data in stats_dict["summary_statistics"]["question_group_summary"].items():
        print(f"  {group_name.title()}:")
        print(f"    Questions: {group_data['total_questions']}")
        print(f"    Avg response rate: {group_data['avg_response_rate']:.1f}%")
        print(f"    High missingness (>50%): {group_data['questions_with_high_missingness']}")
    
    # weights
    weights_info = stats_dict["summary_statistics"]["weights_info"]
    print(f"\nWeights:")
    if weights_info["has_weights"]:
        weight_stats = weights_info["weight_statistics"]
        print(f"  Available: Yes")
        print(f"  Mean weight: {weight_stats['mean']:.3f}")
        print(f"  Weight range: {weight_stats['min']:.3f} - {weight_stats['max']:.3f}")
        print(f"  Total weighted N: {weight_stats['total_weighted_n']:,.0f}")
    else:
        print(f"  Available: No")