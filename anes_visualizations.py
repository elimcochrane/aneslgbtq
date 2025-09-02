import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def get_axis_direction_labels(col_name, data_type):

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
                    n, bins, patches = ax.hist(therm_data, bins=25, alpha=0.8, color=color, edgecolor='black', linewidth=0.8, density=True)
                    ax.set_title(f'{subplot_title}\n(n={len(therm_data):,})', fontsize=11, pad=15, fontweight='bold')
                    
                    yticks = ax.get_yticks()
                    ax.set_yticklabels([f'{tick*100:.1f}%' for tick in yticks])
                    ax.set_ylabel('Percentage (%)', fontsize=9)
                    
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
                percentages = (value_counts.values / len(valid_data)) * 100
                bars = ax.bar(range(len(percentages)), percentages, alpha=0.8, color=color, edgecolor='black', linewidth=0.8)
                ax.set_title(f'{subplot_title}\n(n={len(valid_data):,})', fontsize=11, pad=15, fontweight='bold')
                ax.set_ylabel('Percentage (%)', fontsize=9)
                
                if 'gay_id' in col.lower():
                    orientation_labels = ['Heterosexual', 'Gay/Lesbian', 'Bisexual', 'Other']
                    actual_labels = [orientation_labels[int(val)-1] if int(val) <= len(orientation_labels) else f'Value {int(val)}'
                                     for val in value_counts.index]
                    ax.set_xticks(range(len(percentages)))
                    ax.set_xticklabels(actual_labels, fontsize=9)
                    ax.set_xlabel('Sexual Orientation', fontsize=9, labelpad=5)
                elif len(percentages) >= 2:
                    direction_labels = get_axis_direction_labels(col, 'categorical')
                    ax.set_xticks([0, len(percentages)-1])
                    ax.set_xticklabels(direction_labels, fontsize=9)
                    ax.set_xlabel('Response Scale', fontsize=9, labelpad=5)
                else:
                    ax.set_xticks(range(len(percentages)))
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

def create_comparison_plot(df, col1, col2, title="Comparison Plot", filename="comparison.png"):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    valid_data1 = df[col1].dropna()
    if 'therm' in col1:
        ax1.hist(valid_data1, bins=20, alpha=0.7, color='blue', edgecolor='black', density=True)
        yticks1 = ax1.get_yticks()
        ax1.set_yticklabels([f'{tick*100:.1f}%' for tick in yticks1])
        ax1.set_xlabel('Thermometer Score')
    else:
        value_counts1 = valid_data1.value_counts().sort_index()
        percentages1 = (value_counts1.values / len(valid_data1)) * 100
        ax1.bar(range(len(value_counts1)), percentages1, alpha=0.7, color='blue', edgecolor='black')
        ax1.set_xlabel('Response Category')
    ax1.set_title(create_subplot_title(col1))
    ax1.set_ylabel('Percentage (%)')
    
    valid_data2 = df[col2].dropna()
    if 'therm' in col2:
        ax2.hist(valid_data2, bins=20, alpha=0.7, color='red', edgecolor='black', density=True)
        yticks2 = ax2.get_yticks()
        ax2.set_yticklabels([f'{tick*100:.1f}%' for tick in yticks2])
        ax2.set_xlabel('Thermometer Score')
    else:
        value_counts2 = valid_data2.value_counts().sort_index()
        percentages2 = (value_counts2.values / len(valid_data2)) * 100
        ax2.bar(range(len(value_counts2)), percentages2, alpha=0.7, color='red', edgecolor='black')
        ax2.set_xlabel('Response Category')
    ax2.set_title(create_subplot_title(col2))
    ax2.set_ylabel('Percentage (%)')
    
    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')

def order_visualizations(df, trans_cols, gay_cols):
    trans_order = [
        'trans_id', 'trans_therm', 'trans_contact', 
        'trans_military', 'trans_bathroom', 'trans_discrim',
        'trans_sports_pre', 'trans_sports_post', 'trans_sports'
    ]
    
    gay_order = [
        'gay_id', 'gay_therm', 'gay_contact', 
        'gay_marriage', 'gay_adoption', 'gay_elect', 'gay_discrim'
    ]
    
    def reorder_columns(available_cols, desired_order):
        ordered = [col for col in desired_order if col in available_cols]
        remaining = [col for col in available_cols if col not in desired_order]
        return ordered + remaining
    
    if trans_cols:
        ordered_trans = reorder_columns(trans_cols, trans_order)
        create_single_distribution_plot(df, ordered_trans, 'Transgender Questions', 
                                       'transgender_questions_distribution.png')
    
    if gay_cols:
        ordered_gay = reorder_columns(gay_cols, gay_order)
        create_single_distribution_plot(df, ordered_gay, 'Gay/LGB Questions', 
                                       'gay_lgb_questions_distribution.png')