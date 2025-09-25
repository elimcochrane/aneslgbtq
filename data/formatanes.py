import pandas as pd
import numpy as np
from aneslgbtq.data.dicts import var_dict, ans_dict
from aneslgbtq.data.weights import weights_dict

def anes_lgbt_fixed(input_file='anes_2024.csv', output_file='lgbt_anes.csv'):
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    print(f"Original dataset shape: {df.shape}")

    column_mapping = var_dict
    columns_to_keep = list(column_mapping.keys())
    existing_columns = [col for col in columns_to_keep if col in df.columns]
    missing_columns = [col for col in columns_to_keep if col not in df.columns]

    if missing_columns:
        print(f"\nWarning: {len(missing_columns)} columns not found in dataset:")
        for col in missing_columns[:5]:
            print(f"  - {col}")
        if len(missing_columns) > 5:
            print(f"  ... and {len(missing_columns) - 5} more")

    print(f"\nFiltering dataset to keep {len(existing_columns)} columns...")
    filtered_df = df[existing_columns].copy()

    print(f"\nRenaming {len(existing_columns)} columns based on mapping...")
    filtered_df = filtered_df.rename(columns=column_mapping)

    missing_codes = [-9, -8, -7, -6, -5, -4, -3, -2, -1]
    print(f"\nCleaning missing codes {missing_codes}...")
    
    for col in filtered_df.columns:
        if col not in ['weight_post', 'psu', 'stratum']:
            filtered_df[col] = filtered_df[col].replace(missing_codes, np.nan)

    # weight psu stratum
    print("\nInitializing survey design variables...")
    filtered_df['weight'] = np.nan
    filtered_df['psu'] = np.nan
    filtered_df['stratum'] = np.nan

    print("\nChecking available weight columns...")
    available_weights = {}
    
    for sample_type, info in weights_dict.items():
        weight_col = info.get('weight')
        psu_col = info.get('psu')
        stratum_col = info.get('stratum')
        
        if all(col in df.columns for col in [weight_col, psu_col, stratum_col]):
            available_weights[sample_type] = {
                'weight': weight_col,
                'psu': psu_col,
                'stratum': stratum_col
            }
            print(f"  ✓ {sample_type}: {weight_col}, {psu_col}, {stratum_col}")
        else:
            print(f"  ✗ {sample_type}: Missing columns")

    if not available_weights:
        print("ERROR: No complete weight/PSU/stratum combinations found!")
        return filtered_df

    print(f"\nAssigning weights row-by-row for {len(filtered_df)} respondents...")
    
    weight_cols = []
    psu_cols = []
    stratum_cols = []
    
    for sample_type, cols in available_weights.items():
        weight_cols.append(cols['weight'])
        psu_cols.append(cols['psu'])
        stratum_cols.append(cols['stratum'])
    
    print("Converting weight columns to numeric...")
    for col in weight_cols + psu_cols + stratum_cols:
        df[col] = df[col].replace([' ', '', '  ', '   '], np.nan)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].replace(missing_codes, np.nan)
    
    # priority order for weight assignment (i did most comprehensive to least)
    priority_order = ['ftf_web_papi', 'panel_ftf_web_papi', 'ftf_web_panel', 
                     'ftf_web', 'web_papi', 'panel', 'web', 'ftf']
    
    priority_order = [wt for wt in priority_order if wt in available_weights]
    
    print(f"Using priority order: {priority_order}")
    
    weights_assigned = 0
    assignment_counts = {}
    
    for idx in filtered_df.index:
        assigned = False
        
        for sample_type in priority_order:
            cols = available_weights[sample_type]
            
            weight_val = df.loc[idx, cols['weight']]
            psu_val = df.loc[idx, cols['psu']]
            stratum_val = df.loc[idx, cols['stratum']]
            
            if (pd.notna(weight_val) and pd.notna(psu_val) and pd.notna(stratum_val) and 
                weight_val > 0):
                
                filtered_df.loc[idx, 'weight'] = weight_val
                filtered_df.loc[idx, 'psu'] = psu_val
                filtered_df.loc[idx, 'stratum'] = stratum_val
                
                assignment_counts[sample_type] = assignment_counts.get(sample_type, 0) + 1
                weights_assigned += 1
                assigned = True
                break
        
        if not assigned:
            pass
    
    print(f"\nWeight assignment results:")
    print(f"  Total respondents: {len(filtered_df):,}")
    print(f"  Weights assigned: {weights_assigned:,}")
    print(f"  No weights: {len(filtered_df) - weights_assigned:,}")
    
    print(f"\nBreakdown by survey type:")
    for sample_type, count in assignment_counts.items():
        percentage = (count / len(filtered_df)) * 100
        print(f"  {sample_type}: {count:,} ({percentage:.1f}%)")
    
    print(f"\nFinal weight statistics:")
    valid_weights = filtered_df['weight'].notna().sum()
    if valid_weights > 0:
        print(f"  Valid weights: {valid_weights:,}/{len(filtered_df):,}")
        print(f"  Weight range: {filtered_df['weight'].min():.4f} to {filtered_df['weight'].max():.4f}")
        print(f"  Mean weight: {filtered_df['weight'].mean():.4f}")
        print(f"  Unique PSUs: {filtered_df['psu'].nunique()}")
        print(f"  Unique Strata: {filtered_df['stratum'].nunique()}")
    else:
        print("  ERROR: No valid weights assigned!")
    
    print(f"\nFiltered dataset shape: {filtered_df.shape}")
    print(f"\nFinal column names:")
    for i, col in enumerate(filtered_df.columns):
        print(f"  {i+1:2d}. {col}")

    filtered_df.to_csv(output_file, index=False)
    print(f"\nFiltered dataset saved as '{output_file}'")

    print(f"\nData quality summary:")
    print(f"Number of rows: {len(filtered_df):,}")
    print(f"Number of columns: {len(filtered_df.columns)}")
    
    weight_issues = filtered_df['weight'].isna().sum()
    if weight_issues > 0:
        print(f"{weight_issues:,} respondents without weights")
    else:
        print("All respondents have valid weights")

    return filtered_df

def validate_weights(df, original_df, weights_dict):
    print("Weight Validation")
    
    sample_indices = df.index[:10]
    
    for idx in sample_indices:
        assigned_weight = df.loc[idx, 'weight']
        assigned_psu = df.loc[idx, 'psu']
        assigned_stratum = df.loc[idx, 'stratum']
        
        print(f"\nRow {idx}:")
        print(f"  Assigned weight: {assigned_weight}")
        print(f"  Assigned PSU: {assigned_psu}")
        print(f"  Assigned stratum: {assigned_stratum}")
        
        found_source = False
        for sample_type, cols in weights_dict.items():
            if all(col in original_df.columns for col in [cols['weight'], cols['psu'], cols['stratum']]):
                orig_weight = pd.to_numeric(original_df.loc[idx, cols['weight']], errors='coerce')
                orig_psu = pd.to_numeric(original_df.loc[idx, cols['psu']], errors='coerce')
                orig_stratum = pd.to_numeric(original_df.loc[idx, cols['stratum']], errors='coerce')
                
                if (pd.notna(orig_weight) and pd.notna(orig_psu) and pd.notna(orig_stratum) and
                    abs(orig_weight - assigned_weight) < 0.0001):
                    print(f"  ✓ Source: {sample_type} ({cols['weight']})")
                    found_source = True
                    break
        
        if not found_source and pd.notna(assigned_weight):
            print(f"Could not identify source for assigned weight")

if __name__ == "__main__":
    print("ANES 2024 LGBTQ Data Analysis")

    try:
        original_df = pd.read_csv('anes_2024.csv')
        filtered_data = anes_lgbt_fixed()
        validate_weights(filtered_data, original_df, weights_dict)
        
    except FileNotFoundError:
        print("Error: 'anes_2024.csv' file not found. Please make sure the file is in the current directory.")
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()