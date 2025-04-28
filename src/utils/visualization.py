import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import utils.time as tu

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

def plot_histograms(df, vars, column_names_map, suptitle):
    """Plots the histograms of the specified variables."""
    fig, axes = plt.subplots(3, 4, figsize=(14, 8))
    axes = axes.flatten()
    for i, column in enumerate(vars):
        axes[i].hist(df[column], bins=20, color='pink', edgecolor='black')
        axes[i].set_title(column_names_map[column])
        axes[i].set_xlabel('Value')
        axes[i].set_ylabel('Frequency')
        axes[i].grid()
    if len(vars) < len(axes):
        for j in range(len(vars), len(axes)):
            axes[j].axis("off")
    plt.suptitle(suptitle)
    plt.tight_layout()
    plt.show()

def plot_stacked_histograms(dfs, vars, column_names_map, suptitle):
    """Plots stacked histograms of the specified variables for multiple dataframes."""
    fig, axes = plt.subplots(3, 4, figsize=(14, 8))
    axes = axes.flatten()
    
    colors = ["#0C5174", "#147EB3", "#68C1EE"]
    labels = ['ROCKET BODY', 'DEBRIS', 'PAYLOAD']
    
    for i, column in enumerate(vars):
        data_to_plot = [df[column] for df in dfs]
        
        axes[i].hist(data_to_plot, bins=20, stacked=True, color=colors, edgecolor='black')
        
        axes[i].set_title(column_names_map[column])
        axes[i].set_xlabel('Value')
        axes[i].set_ylabel('Frequency')
        axes[i].grid()
    
    if len(vars) < len(axes):
        for j in range(len(vars), len(axes)):
            axes[j].axis("off")
    
    plt.suptitle(suptitle)
    
    fig.legend(labels, loc='lower right', bbox_to_anchor=(1, 0), fontsize=10)    
    plt.tight_layout()
    plt.show()
def plot_histograms_by_cat(df, num_vars, cat_var, column_names_map, suptitle):
    cat_var_vals = df[cat_var].unique()
    fig, axes = plt.subplots(ncols=len(num_vars), nrows=len(cat_var_vals), figsize=(6*len(num_vars), 4*len(cat_var_vals)))
    for i, num_var in enumerate(num_vars):
        var_min, var_max = df[num_var].min(), df[num_var].max()
        bins = np.linspace(var_min, var_max, 30)
        for j, cat in enumerate(cat_var_vals):
            filter_df = df[df[cat_var]==cat]
            axes[j][i].hist(filter_df[num_var], bins=bins, color=f"C{j}", alpha=0.7, edgecolor="black", label=cat)
            axes[j][i].set_title(column_names_map[num_var])
            axes[j][i].set_xlabel('Value')
            axes[j][i].set_ylabel('Frequency')
            axes[j][i].set_xlim(var_min, var_max)
            axes[j][i].grid(alpha=0.3)
            axes[j][i].legend()
    plt.suptitle(suptitle)
    plt.tight_layout()
    plt.show()

def plot_corr_matrix(df, vars, column_names_map, suptitle):
    """Plots a correlation matrix for the specified variables."""
    tick_labels = [column_names_map[item] for item in vars]
    plt.figure(figsize=(12, 6))
    corr = df[vars].corr()
    sns.heatmap(corr, mask=np.triu(np.ones_like(corr, dtype=bool)), cmap='RdBu', annot=True,
                xticklabels=tick_labels,
                yticklabels=tick_labels
                )
    plt.xticks(rotation=45, ha='right') 
    plt.suptitle(suptitle)
    plt.tight_layout()
    plt.show()

def plot_scatter_by_cat(df, num_var1, num_var2, cat_var1, cat_var2, column_names_map, suptitle, pad_scale=0.1):
    cat_var1_vals, cat_var2_vals = df[cat_var1].unique(), df[cat_var2].unique()
    fig, axes = plt.subplots(nrows=len(cat_var2_vals), ncols=len(cat_var1_vals), figsize=(4*len(cat_var1_vals),3*len(cat_var2_vals)))
    for i, cat1 in enumerate(cat_var1_vals):
        axes[0][i].set_title(cat1)
        sub_df = df[df[cat_var1]==cat1]
        var1_min, var1_max = sub_df[num_var1].min()*(1-pad_scale), sub_df[num_var1].max()*(1+pad_scale)
        var2_min, var2_max = sub_df[num_var2].min()*(1-pad_scale), sub_df[num_var2].max()*(1+pad_scale)
        for j, cat2 in enumerate(cat_var2_vals):
            filter_df = df[(df[cat_var1]==cat1)&(df[cat_var2]==cat2)]
            # Maybe instead of scatterplot use kde?
            axes[j][i].scatter(filter_df[num_var1], filter_df[num_var2], c=f"C{j}", s=3, alpha=0.5, label=cat2)
            # sns.kdeplot(x=filter_df[num_var1], y=filter_df[num_var2], color=f"C{j}", ax=axes[j][i])
            axes[j][i].legend(loc="upper right")
            axes[j][i].grid(alpha=0.3)
            axes[j][i].set_xlim(var1_min, var1_max)
            axes[j][i].set_ylim(var2_min, var2_max)
            axes[j][i].set_xlabel(column_names_map[num_var1])
            axes[j][i].set_ylabel(column_names_map[num_var2])
    
    plt.suptitle(suptitle)
    plt.tight_layout()
    
def pca_pc1_pc2_pair(pca_result, labels, label_info, suptitle, x_range=None, y_range=None):
    '''pca first and second components full range and zoom range'''
    type_labels, type_categories = pd.factorize(labels)
    
    _, ax = plt.subplots(1, 2, figsize=(18, 7))
    scatter = ax[0].scatter(pca_result[:, 0], pca_result[:, 1], c=type_labels, cmap='tab10', alpha=0.7, edgecolors='none')
    ax[0].set_xlabel("PC 1")
    ax[0].set_ylabel("PC 2")
    ax[0].set_title("Entire Range of Data")
    ax[0].grid(True)
    legend_labels = {i: type_categories[i] for i in range(len(type_categories))}
    handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=scatter.cmap(scatter.norm(i)), markersize=10) 
               for i in legend_labels]
    ax[0].legend(handles, legend_labels.values(), title=label_info)

    # Zoomed-in PCA plot on the right
    ax[1].scatter(pca_result[:, 0], pca_result[:, 1], c=type_labels, cmap='tab10', alpha=0.7, edgecolors='none')
    ax[1].set_xlabel("PC 1")
    ax[1].set_ylabel("PC 2")
    ax[1].set_title(f"Zoomed-in View (Range: {x_range}, {y_range})")
    ax[1].grid(True)
    if x_range is not None:
        ax[1].set_xlim(x_range)
    if y_range is not None:
        ax[1].set_ylim(y_range)

    ax[1].legend(handles, legend_labels.values(), title=label_info)

    plt.suptitle(suptitle)
    plt.tight_layout()
    plt.show()
    
def plot_side_my_side_confusion(figure, left_train, left_pred, left_title, right_train, right_pred, right_title, label_encoder):
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    train_cm = confusion_matrix(left_train, left_pred, normalize="true")
    train_cm_disp = ConfusionMatrixDisplay(train_cm, display_labels=label_encoder.classes_)
    train_cm_disp.plot(cmap="Reds", ax=ax1)
    ax1.set_title(left_title)
    val_cm = confusion_matrix(right_train, right_pred, normalize="true")
    val_cm_disp = ConfusionMatrixDisplay(val_cm, display_labels=label_encoder.classes_)
    val_cm_disp.plot(cmap="Blues", ax=ax2)
    ax2.set_title(right_title)
    plt.suptitle(figure)
    plt.tight_layout()
    
def plot_state_count_side_by_side(figure, left_title,right_title, df_final, df_payload,df_rb,df_debris ):
    # Visualize number of states per object
    fig, axs = plt.subplots(1, 2, figsize=(10, 4))

    axs[0].hist(df_final['NUMBER'].value_counts().values, bins=49, edgecolor='black', color='#3FA6DA')
    axs[0].set_title(left_title)
    axs[0].set_xlabel("State Count [per object]")
    axs[0].set_ylabel("Frequency")
    axs[0].grid(True)

    axs[1].hist([df_rb['NUMBER'].value_counts().values,
                df_payload['NUMBER'].value_counts().values,
                df_debris['NUMBER'].value_counts().values], 
                bins=49, edgecolor='black', stacked=True, 
                color=["#0C5174", "#147EB3", "#68C1EE"], 
                label=['Rocket Body', 'Payload', 'Debris'])
    axs[1].set_title(right_title)
    axs[1].set_xlabel("State Count [per object]")
    axs[1].set_ylabel("Frequency")
    axs[1].legend()
    axs[1].grid(True)

    plt.suptitle(figure)
    plt.tight_layout()
    plt.show()
    
def plot_epoch_dists(figure, left_title, right_title, df_final):
    # Visualize distribution of earliest/latest state times and time ranges of states per object
    df_epoch_min_max = df_final.groupby('NUMBER')['EPOCH'].agg(['min', 'max']).reset_index()
    df_epoch_min_max['min_datetime'] = df_epoch_min_max['min'].apply(tu.year_doy_to_datetime)
    df_epoch_min_max['max_datetime'] = df_epoch_min_max['max'].apply(tu.year_doy_to_datetime)
    num_bins = 40
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.hist(df_epoch_min_max['min_datetime'], bins=num_bins, alpha=0.5, label='First Epoch', density=True)
    ax1.hist(df_epoch_min_max['max_datetime'], bins=num_bins, alpha=0.5, label='Last Epoch', density=True, color='red')

    ax1.set_xlabel('Epoch Time')
    ax1.set_ylabel('Density')
    ax1.set_title(left_title)
    ax1.tick_params(axis='x', rotation=45, labelrotation=45)
    ax1.grid(True)
    ax1.legend()

    ax2.hist((df_epoch_min_max['max_datetime'] - df_epoch_min_max['min_datetime']).dt.days,
            bins=num_bins, alpha=0.5, density=True)

    ax2.set_xlabel('Days')
    ax2.set_ylabel('Density')
    ax2.set_title(right_title)
    ax2.grid(True)

    plt.suptitle(figure)
    plt.tight_layout()
    plt.show()
    
def plot_state_count_ratio(title, df_final):
    rso2count = df_final['NUMBER'].value_counts()
    thresholds = list(range(1,50))
    rat = []
    for t in thresholds:
        rsos_geq_threshold = rso2count[rso2count.values >= t].index
        rat.append(len(rsos_geq_threshold)/len(rso2count.values ))
        
    plt.axhline(y=.5, color='red', linestyle='--')
    plt.text(1, .5, "50% of Data", color='red', ha='left', va='bottom')
    plt.plot(thresholds, rat)
    plt.title(title)
    plt.xlabel('Threshold [Number of States]')
    plt.ylabel('Proportion of Objects from Total')
    plt.grid()
    plt.show()

def plot_epoch_history(history, suptitle):

    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(10,4))
    ax1.plot(np.arange(len(history["loss"]))+1, history["loss"], label="Train")
    ax1.plot(np.arange(len(history["val_loss"]))+1, history["val_loss"], label="Validation")
    ax1.grid(alpha=0.3)
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("Categorical Crossentropy Loss")
    ax1.legend()
    ax2.plot(np.arange(len(history["accuracy"]))+1, history["accuracy"], label="Train")
    ax2.plot(np.arange(len(history["val_accuracy"]))+1, history["val_accuracy"], label="Validation")
    ax2.grid(alpha=0.3)
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("Accuracy")
    ax2.legend()

    plt.suptitle(suptitle)
    plt.tight_layout()



def pretty_column_names():
    return {
        'TYPE': 'Object Type',
        'NAME': 'Name',
        'RCS': 'Radar Cross Section',
        'IS_CURRENT': 'Not Decayed', 
        'REGIME': 'Regime',
        'EPOCH': 'Epoch',
        'COUNTRY': 'Country Code',
        'LINE1': 'TLE Line 1',
        'LINE2': 'TLE Line 2',
        'INCL': 'Inclination',
        'RAAN': 'Right Asc. of the Asc. Node (RAAN)',
        'ECC': 'Eccentricity',
        'ARG_PER': 'Argument of Perigee',
        'MEAN_MOTION': 'Mean Motion (Rev/Day)',
        'MEAN_ANOM': 'Mean Anomaly',
        'SMA_KM': 'Semi-Major Axis (SMA)',
        'APOGEE_KM': 'Apogee',
        'PERIGEE_KM': 'Perigee',
        'MEAN_MOTION_1ST_DER': 'First Derivative of Mean Motion',  
        'MEAN_MOTION_2ND_DER': 'Second Derivative of Mean Motion', 
        'B_STAR': 'B* (Drag Term)'
    }
