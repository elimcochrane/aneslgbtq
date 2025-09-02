import pandas as pd
from dicts import var_dict, ans_dict, theme_dict
from anes_statistics import load_and_prepare_data, basic_descriptive_stats, samplics_analysis
from anes_visualizations import create_comparison_plot, order_visualizations
from anes_descriptives import generate_descriptive_json, print_summary_report, save_descriptive_json

def main_analysis(csv_file_path):
    df, column_mapping = load_and_prepare_data(csv_file_path, var_dict)
    trans_cols, gay_cols, demo_cols = basic_descriptive_stats(df, theme_dict)
    samplics_results = samplics_analysis(df)
    descriptive_stats = generate_descriptive_json(
        df, 
        trans_cols=trans_cols, 
        gay_cols=gay_cols, 
        output_file="anes_descriptive_stats.json"
    )
    order_visualizations(df, trans_cols, gay_cols)
    
    return df, samplics_results, descriptive_stats

def analyze_specific_questions(df, descriptive_stats):
    """
    Example of how to extract specific question statistics from the JSON
    
    Args:
        df (DataFrame): Survey data
        descriptive_stats (dict): JSON descriptive statistics
    """
    
    # Example 1: Get transgender identification statistics
    if 'trans_id' in descriptive_stats['transgender_questions']['questions']:
        trans_id_stats = descriptive_stats['transgender_questions']['questions']['trans_id']
        # Process transgender identification data
        
        if 'value_counts' in trans_id_stats:
            # Process response breakdown
            for value, count in trans_id_stats['value_counts'].items():
                percentage = trans_id_stats['percentages'][value]
    
    # Example 2: Get thermometer statistics
    if 'trans_therm' in descriptive_stats['transgender_questions']['questions']:
        trans_therm_stats = descriptive_stats['transgender_questions']['questions']['trans_therm']
        # Process thermometer statistics
        mean_score = trans_therm_stats['mean']
        median_score = trans_therm_stats['median']
        
        if 'weighted_mean' in trans_therm_stats:
            weighted_mean = trans_therm_stats['weighted_mean']

def export_results_summary(descriptive_stats, output_file="analysis_summary.txt"):
    """
    Export a text summary of key findings
    
    Args:
        descriptive_stats (dict): JSON descriptive statistics
        output_file (str): Output filename
    """
    
    with open(output_file, 'w') as f:
        metadata = descriptive_stats['metadata']
        f.write(f"Analysis Date: {metadata['analysis_date']}\n")
        f.write(f"Total Respondents: {metadata['total_respondents']:,}\n")
        f.write(f"Total Variables: {metadata['total_variables']}\n\n")
        
        # key findings for each group
        for group_name in ['transgender_questions', 'gay_lgb_questions']:
            group_data = descriptive_stats[group_name]
            f.write(f"{group_data['group_info']['name']} Questions:\n")
            f.write(f"  Total questions: {group_data['group_info']['total_questions']}\n")
            f.write(f"  Questions with data: {group_data['group_info']['questions_with_data']}\n")
            
            # Find highest and lowest response rate questions
            if group_data['questions']:
                response_rates = {q: stats['response_rate'] 
                                for q, stats in group_data['questions'].items()}
                highest = max(response_rates, key=response_rates.get)
                lowest = min(response_rates, key=response_rates.get)
                
                f.write(f"  Highest response rate: {highest} ({response_rates[highest]:.1f}%)\n")
                f.write(f"  Lowest response rate: {lowest} ({response_rates[lowest]:.1f}%)\n")
            f.write("\n")
    
    # Summary exported successfully

if __name__ == "__main__":
    # Main execution
    csv_file = "lgbt_anes.csv"
    
    try:
        # Run main analysis
        df, samplics_results, descriptive_stats = main_analysis(csv_file)
        
        # Analyze specific questions
        analyze_specific_questions(df, descriptive_stats)
        
        # Export summary
        export_results_summary(descriptive_stats)
        
    except Exception as e:
        # Error during analysis
        pass