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

def plot_categorical_comparison(df1, df2, categorical_vars, title1, title2, proportion=True):
    """Function that plots the distribution of categorical variables for two dataframes."""
    fig, axes = plt.subplots(ncols=2, nrows=len(categorical_vars), figsize=(10,len(categorical_vars)*3), sharey=True)
    for ax, var in zip(axes, categorical_vars):
        for i, (df, title) in enumerate(zip([df1, df2], [title1, title2])):
            data = df[var].value_counts(normalize=proportion)
            if var == "COUNTRY":
                data = group_small_categories(data)
            data.plot(kind='bar', alpha=0.7, color=f'C{i}', ax=ax[i])
            ax[i].set_xlabel(var)
            ax[i].set_ylabel('Proportion' if proportion else 'Count')
            ax[i].tick_params(axis='x', labelrotation=0)  
            ax[i].grid(alpha=0.3)
    axes[0][0].set_title(title1)
    axes[0][1].set_title(title2)
    plt.tight_layout()

def plot_numeric_comparison(df1, df2, numeric_vars, title1, title2):
    """Function that plots the distribution of continuous variables for two dataframes."""
    fig, axes = plt.subplots(ncols=2, nrows=len(numeric_vars), figsize=(10,len(numeric_vars)*3))
    for ax, var in zip(axes, numeric_vars):
        x_min = min(df1[var].min(), df2[var].min())
        x_max = max(df1[var].max(), df2[var].max())
        for i, (df, title) in enumerate(zip([df1, df2], [title1, title2])):
            data = df[var]
            sns.kdeplot(data, color=f"C{i}", ax=ax[i])
            ax[i].set_xlim(x_min, x_max)
            ax[i].set_xlabel(var)
            ax[i].set_ylabel('Density')
            ax[i].tick_params(axis='x', labelrotation=0)  
            ax[i].grid(alpha=0.3)
    axes[0][0].set_title(title1)
    axes[0][1].set_title(title2)
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