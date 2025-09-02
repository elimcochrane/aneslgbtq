import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from samplics.estimation import TaylorEstimator
from samplics.utils.types import PopParam
from dicts import var_dict, ans_dict, theme_dict

value_meanings = ans_dict
trans_questions = list(theme_dict['trans_qs'])
gay_questions = list(theme_dict['gay_qs'])

def load_and_prepare_data(csv_file_path):
    column_mapping = var_dict
    df = pd.read_csv(csv_file_path)
    existing_cols = {old: new for old, new in column_mapping.items() if old in df.columns}
    df_renamed = df.rename(columns=existing_cols)
    print(f"Successfully loaded {len(df_renamed)} respondents")
    print(f"Mapped {len(existing_cols)} columns")
    return df_renamed, column_mapping

def basic_descriptive_stats(df):
    trans_cols = [col for col in trans_questions if col in df.columns]
    gay_cols = [col for col in gay_questions if col in df.columns]
    demo_cols = [col for col in df.columns if col.startswith('resp_')]

    for group_name, cols in [("Transgender Questions", trans_cols), 
                             ("Gay/LGB Questions", gay_cols), 
                             ("Demographics", demo_cols)]:
        if cols:
            print(f"\n{group_name}:")
            for col in cols:
                valid_count = df[col].notna().sum()
                missing_count = df[col].isna().sum()
                print(f"  {col}: {valid_count} valid, {missing_count} missing")
    return trans_cols, gay_cols, demo_cols

def samplics_analysis(df):
    print("\nEnhanced Samplics Analysis with TaylorEstimator (weights only)")
    weights = df['weight'] if 'weight' in df.columns else pd.Series(1.0, index=df.index)
    print("Using weight column from dataframe")

    analysis_vars = [col for col in df.columns if col != 'weight']
    results = {}

    for var in analysis_vars:
        valid_mask = df[var].notna() & weights.notna()
        if valid_mask.sum() <= 10:
            continue
        try:
            if "therm" in var:
                taylor_est = TaylorEstimator(PopParam.mean)
                mean_est = taylor_est.estimate(
                    y=df.loc[valid_mask, var],
                    samp_weight=weights.loc[valid_mask],
                    remove_nan=True
                )
                results[var] = {
                    "type": "continuous",
                    "mean": mean_est.point_est,
                    "se": mean_est.stderror,
                    "n": valid_mask.sum()
                }
                print(f"\n{var} (Continuous): {mean_est.point_est:.2f} ± {mean_est.stderror:.3f}")
            else:
                categories = df.loc[valid_mask, var].dropna().unique()
                cat_results = {}
                for cat in categories:
                    y_binary = (df.loc[valid_mask, var] == cat).astype(int)
                    taylor_est = TaylorEstimator(PopParam.ratio)
                    prop_est = taylor_est.estimate(
                        y=y_binary,
                        samp_weight=weights.loc[valid_mask],
                        remove_nan=True
                    )
                    cat_results[cat] = {
                        "proportion": prop_est.point_est,
                        "se": prop_est.stderror
                    }
                results[var] = {
                    "type": "categorical",
                    "categories": cat_results,
                    "n": valid_mask.sum()
                }
                print(f"\n{var} (Categorical): {', '.join([f'{k}:{v['proportion']:.2f}' for k,v in cat_results.items()])}")
        except Exception as e:
            print(f"Error analyzing {var}: {e}")

    return results

def get_axis_direction_labels(col_name, data_type):
    """
    Generate directional labels for x-axis endpoints based on specific ANES LGBTQ+ questions
    """
    col_lower = col_name.lower()
    
    if data_type == 'thermometer':
        return ['Cold', 'Warm']
    
    question_mappings = {
        'trans_id': ['Yes', 'No'],  # 1=Yes, 2=No
        'trans_contact': ['Yes', 'No'],  # 1=Yes, 2=No
        'trans_military': ['Favor Greatly', 'Oppose Greatly'],  # 1=Favor a great deal, 7=Oppose a great deal
        'trans_bathroom': ['Favor Greatly', 'Oppose Greatly'],  # 1=Favor a great deal, 7=Oppose a great deal
        'trans_sports': ['Favor Greatly', 'Oppose Greatly'],  # 1=Favor a great deal, 7=Oppose a great deal
        'trans_discrim': ['Great Deal', 'None at All'],  # 1=A great deal, 5=None at all
        'gay_id': ['Straight', 'Other'],  # 1=Heterosexual, 2-4=Other orientations
        'gay_contact': ['Yes', 'No'],  # 1=Yes, 2=No
        'gay_adoption': ['Strongly Permit', 'Strongly Forbid'],  # 1=Very strongly permit, 6=Very strongly not permit
        'gay_marriage': ['Favor Greatly', 'Oppose Greatly'],  # 1=Favor a great deal, 7=Oppose a great deal
        'gay_elect': ['Extremely Important', 'Not Important'],  # 1=Extremely important, 5=Not at all important
        'gay_discrim': ['Favor Strongly', 'Oppose Strongly']  # 1=Favor strongly, 4=Oppose strongly
    }
    
    for question_key, labels in question_mappings.items():
        if question_key in col_lower:
            return labels
    
    return ['Low', 'High']

def create_subplot_title(col_name):
    title = col_name.replace('_', ' ').title()
    title = title.replace('Resp ', '').replace('Gay ', '').replace('Trans ', '')
    title = title.replace('Therm', 'Feeling Thermometer')
    return title

def create_single_distribution_plot(df, question_cols, title, filename, figsize_per_plot=(6, 5)):
    plt.style.use('default')
    sns.set_palette("husl")
    existing_cols = [col for col in question_cols if col in df.columns]
    if not existing_cols:
        print(f"No questions found for {title}!")
        return

    n_cols = min(3, len(existing_cols))
    n_rows = (len(existing_cols) + n_cols - 1) // n_cols
    fig_width = figsize_per_plot[0] * n_cols + 2 
    fig_height = figsize_per_plot[1] * n_rows + 3
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(fig_width, fig_height))
    axes = np.atleast_1d(axes).ravel()
    fig.suptitle(f'{title} - Distribution of Responses', fontsize=18, y=0.96, fontweight='bold')
    colors = ['firebrick', 'orange', 'gold', 'green', 'lightseagreen', 'cornflowerblue', 'rebeccapurple', 'orchid', 'saddlebrown']

    for idx, col in enumerate(existing_cols):
        ax = axes[idx]
        color = colors[idx % len(colors)]
        valid_data = df[col].dropna()
        
        subplot_title = create_subplot_title(col)
        
        if len(valid_data) > 0:
            if 'therm' in col:
                therm_data = valid_data[(valid_data >= 0) & (valid_data <= 100)]
                if len(therm_data) > 0:
                    ax.hist(therm_data, bins=25, alpha=0.8, color=color, edgecolor='black', linewidth=0.8)
                    ax.set_title(f'{subplot_title}\n(n={len(therm_data):,})', fontsize=11, pad=15, fontweight='bold')
                    
                    direction_labels = get_axis_direction_labels(col, 'thermometer')
                    ax.set_xticks([0, 100])
                    ax.set_xticklabels(direction_labels, fontsize=9)
                    ax.set_xlabel('Feeling', fontsize=9, labelpad=5)
                else:
                    ax.text(0.5, 0.5, 'No valid data', ha='center', va='center', transform=ax.transAxes, fontsize=12, color='red')
                    ax.set_title(f'{subplot_title}', fontsize=11, pad=15, fontweight='bold')
            else:
                value_counts = valid_data.value_counts().sort_index()
                labels = [f'Value {int(val)}' for val in value_counts.index]
                values = value_counts.values
                bars = ax.bar(range(len(values)), values, alpha=0.8, color=color, edgecolor='black', linewidth=0.8)
                ax.set_title(f'{subplot_title}\n(n={len(valid_data):,})', fontsize=11, pad=15, fontweight='bold')
                
                if len(values) >= 2:
                    direction_labels = get_axis_direction_labels(col, 'categorical')
                    ax.set_xticks([0, len(values)-1])
                    ax.set_xticklabels(direction_labels, fontsize=9)
                    ax.set_xlabel('Response Scale', fontsize=9, labelpad=5)
                else:
                    ax.set_xticks(range(len(values)))
                    ax.set_xticklabels(labels, fontsize=9)
        else:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', transform=ax.transAxes, fontsize=12, color='red')
            ax.set_title(f'{subplot_title}', fontsize=11, pad=15, fontweight='bold')
        
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    for idx in range(len(existing_cols), len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout(rect=[0, 0.02, 1, 0.94], pad=3.0, h_pad=4.0, w_pad=3.0)
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()
    print(f"Saved visualization: {filename}")

def create_distribution_visualizations(df, trans_cols, gay_cols):
    if trans_cols:
        create_single_distribution_plot(df, trans_cols, 'Transgender Questions', 'transgender_questions_distribution.png')
    if gay_cols:
        create_single_distribution_plot(df, gay_cols, 'Gay/LGB Questions', 'gay_lgb_questions_distribution.png')

def main(csv_file_path):
    print("ANES LGBTQ+ SURVEY DATA - DESCRIPTIVE STATISTICS")
    df, column_mapping = load_and_prepare_data(csv_file_path)
    trans_cols, gay_cols, demo_cols = basic_descriptive_stats(df)
    results = samplics_analysis(df)
    create_distribution_visualizations(df, trans_cols, gay_cols)
    return df, results

if __name__ == "__main__":
    csv_file = "lgbt_anes.csv"
    df, results = main(csv_file)
    print("Done")