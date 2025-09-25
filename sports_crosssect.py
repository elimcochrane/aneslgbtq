import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def main():
    df = pd.read_csv("lgbt_anes.csv")
    print(f"Total respondents: {len(df):,}")
    
    print(f"\nData Structure:")
    
    # check structure
    pre_only = df['trans_sports_pre'].notna() & df['trans_sports_post'].isna()
    post_only = df['trans_sports_post'].notna() & df['trans_sports_pre'].isna()
    both = df['trans_sports_pre'].notna() & df['trans_sports_post'].notna()
    
    print(f"Pre-election only: {pre_only.sum():,}")
    print(f"Post-election only: {post_only.sum():,}")
    print(f"Both (true panel): {both.sum():,}")
    
    # create separate datasets for analysis
    pre_data = df[df['trans_sports_pre'].notna()]['trans_sports_pre']
    post_data = df[df['trans_sports_post'].notna()]['trans_sports_post']
    
    if len(pre_data) == 0 or len(post_data) == 0:
        print("Cannot compare - missing pre or post data!")
        return
    
    print(f"\n=Cross-Sectional Comparison:")
    print(f"Pre-election sample: {len(pre_data):,} respondents")
    print(f"Post-election sample: {len(post_data):,} respondents")
    
    # desc stats
    pre_mean = pre_data.mean()
    post_mean = post_data.mean()
    difference = post_mean - pre_mean
    
    print(f"\nPre-election mean: {pre_mean:.2f}")
    print(f"Post-election mean: {post_mean:.2f}")
    print(f"Difference (post - pre): {difference:.3f}")
    print(f"Scale: 1=Favor a ban greatly, 7=Oppose a ban greatly")
    
    if difference > 0:
        direction = "MORE OPPOSITION post-election"
    elif difference < 0:
        direction = "MORE SUPPORT post-election"
    else:
        direction = "NO CHANGE"
    
    print(f"Direction: {direction}")
    
    # t-test and p-value
    t_stat, p_value = stats.ttest_ind(pre_data, post_data)
    print(f"\nStatistical test (t-test):")
    print(f"t-statistic: {t_stat:.3f}")
    print(f"p-value: {p_value:.3f}")
    if p_value < 0.05:
        print("Result: Statistically significant difference")
    else:
        print("Result: No statistically significant difference")
    
    # distributions
    print(f"\nResponse Distributions:")
    print("Pre-election:")
    pre_dist = pre_data.value_counts().sort_index()
    for val, count in pre_dist.items():
        pct = count / len(pre_data) * 100
        print(f"  Response {val}: {count:,} ({pct:.1f}%)")
    
    print("\nPost-election:")
    post_dist = post_data.value_counts().sort_index()
    for val, count in post_dist.items():
        pct = count / len(post_data) * 100
        print(f"  Response {val}: {count:,} ({pct:.1f}%)")
    
    # calculate effect size (Cohen's d)
    pooled_std = np.sqrt(((len(pre_data)-1)*pre_data.std()**2 + (len(post_data)-1)*post_data.std()**2) / (len(pre_data)+len(post_data)-2))
    cohens_d = difference / pooled_std
    print(f"\nEffect size (Cohen's d): {cohens_d:.3f}")
    if abs(cohens_d) < 0.2:
        effect_size = "small"
    elif abs(cohens_d) < 0.5:
        effect_size = "small to medium"
    elif abs(cohens_d) < 0.8:
        effect_size = "medium to large"
    else:
        effect_size = "large"
    print(f"Effect size interpretation: {effect_size}")
    
    # visualizations
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # bar chart
    all_values = sorted(set(pre_data.unique()) | set(post_data.unique()))
    pre_pcts = [pre_dist.get(val, 0) / len(pre_data) * 100 for val in all_values]
    post_pcts = [post_dist.get(val, 0) / len(post_data) * 100 for val in all_values]
    
    x = np.arange(len(all_values))
    width = 0.35
    ax1.bar(x - width/2, pre_pcts, width, label='Pre-election', color='red', alpha=0.7)
    ax1.bar(x + width/2, post_pcts, width, label='Post-election', color='blue', alpha=0.7)
    ax1.set_xlabel('Response')
    ax1.set_ylabel('Percentage')
    ax1.set_title('Response Percentages Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(all_values)
    ax1.legend()
    
    # mean comparison with confidence intervals
    pre_ci = stats.t.interval(0.95, len(pre_data)-1, loc=pre_mean, scale=stats.sem(pre_data))
    post_ci = stats.t.interval(0.95, len(post_data)-1, loc=post_mean, scale=stats.sem(post_data))
    
    ax2.errorbar([1, 2], [pre_mean, post_mean], 
                yerr=[[pre_mean-pre_ci[0], post_mean-post_ci[0]], 
                      [pre_ci[1]-pre_mean, post_ci[1]-post_mean]], 
                fmt='o', capsize=5, capthick=2, markersize=8)
    ax2.set_xlim(0.5, 2.5)
    ax2.set_xticks([1, 2])
    ax2.set_xticklabels(['Pre-election', 'Post-election'])
    ax2.set_ylabel('Mean Response')
    ax2.set_title('Mean Comparison with 95% CI')
    ax2.set_ylim(1, 7)
    
    plt.suptitle('Transgender Sports: Pre vs Post Election Comparison', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.show()
    
    # summary
    print(f"\nSummary:")
    print(f"Pre-election sample: {len(pre_data):,} people, mean = {pre_mean:.2f}")
    print(f"Post-election sample: {len(post_data):,} people, mean = {post_mean:.2f}")
    print(f"Change: {difference:+.3f} ({direction})")
    print(f"Statistical significance: {'Yes' if p_value < 0.05 else 'No'} (p = {p_value:.3f})")
    print(f"Effect size: {effect_size} (d = {cohens_d:.3f})")
    
    return {'pre_data': pre_data, 'post_data': post_data, 'difference': difference, 'p_value': p_value}

if __name__ == "__main__":
    results = main()