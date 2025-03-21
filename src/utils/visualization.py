import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def group_small_categories(series, threshold=0.01, other_label='OTHER'):
    """Helper function that groups together variables with very small proportions."""
    small = series[series < threshold]
    large = series[series >= threshold]
    grouped = large.copy()
    grouped[other_label] = small.sum()
    return grouped.sort_values(ascending=False)

def plot_cat_vars_rcs(df_na_rcs_no_dup, df_w_rcs_no_dup, cat_vars, proportion=True):
    """Function that plots the distribution of categorical variables for those with and without RCS information."""
    fig, axes = plt.subplots(ncols=2, nrows=4, figsize=(12,12), sharey=True)
    for ax, var in zip(axes, cat_vars):
        for i, df in enumerate([df_na_rcs_no_dup, df_w_rcs_no_dup]):
            data = df[var].value_counts(normalize=proportion)
            if var == "COUNTRY":
                data = group_small_categories(data)
            data.plot(kind='bar', alpha=0.7, color=f'C{i}', ax=ax[i])
            ax[i].set_title(f'{var.title()} Counts of Objects with{'out' if i == 0 else ''} RCS')
            ax[i].set_xlabel(var.title())
            ax[i].set_ylabel('Proportion' if proportion else 'Count')
            ax[i].tick_params(axis='x', labelrotation=0)  
            ax[i].grid(alpha=0.3)
    plt.tight_layout()

def plot_cont_vars_rcs(df_na_rcs_no_dup, df_w_rcs_no_dup, cont_vars):
    """Function that plots the distribution of continuous variables for those with and without RCS information."""
    fig, axes = plt.subplots(ncols=2, nrows=len(cont_vars), figsize=(10,len(cont_vars)*3))
    for ax, var in zip(axes, cont_vars):
        x_min = min(df_na_rcs_no_dup[var].min(), df_w_rcs_no_dup[var].min())
        x_max = max(df_na_rcs_no_dup[var].max(), df_w_rcs_no_dup[var].max())
        for i, df in enumerate([df_na_rcs_no_dup, df_w_rcs_no_dup]):
            data = df[var]
            sns.kdeplot(data, color=f"C{i}", ax=ax[i])
            ax[i].set_title(f'{var} for Objects with{'out' if i == 0 else ''} RCS')
            ax[i].set_xlim(x_min, x_max)
            ax[i].set_xlabel(var)
            ax[i].set_ylabel('Density')
            ax[i].tick_params(axis='x', labelrotation=0)  
            ax[i].grid(alpha=0.3)
    plt.tight_layout()

def plot_var_count_by_cat(df, var, cat):
    """Plots the counts of the variable by the specified category."""
    categories = df[cat].unique()
    fig, axes = plt.subplots(ncols=4, figsize=(5*len(categories), 6), sharey=True)
    for i, (ax, category) in enumerate(zip(axes, categories)):
        data = df[df[cat]==category].value_counts(var)
        data.plot(kind='bar', color=f"C{i}", alpha=0.7, title=category, ax=ax)
        ax.grid(alpha=0.7)
    plt.tight_layout()