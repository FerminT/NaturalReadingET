import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
import argparse
from pathlib import Path
from Code.data_processing.utils import get_dirs, get_files, log, load_profile

""" Script to perform analysis on the extracted eye-tracking measures. """


def plot_skills_effects(et_measures, save_path):
    skills_threshold = {'low': 6, 'medium': 9, 'high': 10}
    et_measures['reading_skill'] = et_measures['reading_skill'].apply(lambda x: 'low' if x <= skills_threshold['low']
                                                                        else 'medium' if x <= skills_threshold['medium']
                                                                        else 'high')
    skip_count = count_by_skill(et_measures, 'skipped')
    plot_boxplots('reading_skill', measures=['skipped'], data=skip_count,
                    x_label='Reading skill', ax_titles=['Mean number of skips'],
                    fig_title='Reading skill on skipping', save_path=save_path / 'skills_on_rates.png')
    et_measures_no_skipped = log_normalize_durations(remove_skipped_words(et_measures))
    plot_boxplots('reading_skill', measures=['FFD', 'FPRT'], data=et_measures_no_skipped,
                    x_label='Reading skill', ax_titles=['First Fixation Duration', 'Gaze Duration'],
                    fig_title='Reading skill on early effects', save_path=save_path / 'skills_effects.png')
    fix_count = count_by_skill(et_measures_no_skipped, 'FC')
    regression_count = count_by_skill(et_measures_no_skipped, 'RC')
    fix_count['RC'] = regression_count['RC']
    plot_boxplots('reading_skill', measures=['FC', 'RC'], data=fix_count,
                    x_label='Reading skill', ax_titles=['Fixation count', 'Regression count'],
                    fig_title='Reading skill on fix and regression count', save_path=save_path / 'skills_fixations.png')


def do_analysis(items_paths, words_freq_file, stats_file, subjs_reading_skills, save_path):
    words_freq, items_stats = pd.read_csv(words_freq_file), pd.read_csv(stats_file, index_col=0)
    et_measures = load_et_measures(items_paths, words_freq, subjs_reading_skills)
    save_path.mkdir(parents=True, exist_ok=True)

    print_stats(et_measures, items_stats, save_path)

    et_measures = remove_excluded_words(et_measures)
    plot_skills_effects(et_measures, save_path)
    plot_aggregated_measures(et_measures, save_path)
    et_measures_no_skipped = remove_skipped_words(et_measures)
    plot_ffd_histogram(et_measures_no_skipped)
    et_measures_log = log_normalize_durations(et_measures_no_skipped)
    plot_early_effects(et_measures_log, save_path)

    mlm_analysis(log_normalize_durations(et_measures), words_freq)


def print_stats(et_measures, items_stats, save_path):
    items = items_stats.index.to_list()[:-1]
    processed_stats = {item: {} for item in items}
    for item in items:
        item_measures = et_measures[et_measures['item'] == item]
        n_subjs = len(item_measures['subj'].unique())
        processed_stats[item]['subjs'] = n_subjs
        processed_stats[item]['words'] = len(item_measures[~item_measures['excluded']]['word']) // n_subjs
        processed_stats[item]['words_excluded'] = item_measures['excluded'].sum() // n_subjs
        processed_stats[item]['fix'] = item_measures['FC'].sum()
        processed_stats[item]['fix_excluded'] = items_stats.loc[item, 'n_fix'] - processed_stats[item]['fix']
        processed_stats[item]['regressions'] = item_measures['RC'].sum()
        processed_stats[item]['skips'] = item_measures['skipped'].sum()
        processed_stats[item]['out_of_bounds'] = items_stats.loc[item, 'out_of_bounds']
        processed_stats[item]['return_sweeps'] = items_stats.loc[item, 'return_sweeps']

    processed_stats = pd.DataFrame.from_dict(processed_stats, orient='index', dtype='Int64')
    processed_stats.loc['Total'] = processed_stats.sum()
    print(processed_stats.to_string())

    processed_stats.to_csv(save_path / 'trials_stats.csv')


def mlm_analysis(et_measures, words_freq):
    # This is a crossed random intercept (NOT slope) model with no independent groups
    et_measures['group'] = 1
    et_measures['word_len'] = et_measures['word'].apply(lambda x: 1 / len(x) if x else 0)
    et_measures['word_freq'] = et_measures['word'].apply(lambda x:
                                                         log(words_freq.loc[words_freq['word'] == x, 'cnt'].values[0])
                                                         if x in words_freq['word'].values else 0)

    variance_components = {'subj': '0 + C(subj)', 'item': '0 + C(item)'}
    skipped_formula = 'skipped ~ word_len'
    mixedlm_fit_and_save(skipped_formula, vc_formula=variance_components, re_formula='0', group='group',
                         data=et_measures, centre=False, name='skipped_mlm', family='binomial', save_path=save_path)
    et_measures = remove_skipped_words(et_measures)
    ffd_formula = 'FFD ~ word_len + word_freq'
    fprt_formula = 'FPRT ~ word_len + word_freq'
    mixedlm_fit_and_save(ffd_formula, vc_formula=variance_components, re_formula='0', group='group',
                         data=et_measures, centre=True, name='ffd_mlm', family='mlm', save_path=save_path)
    mixedlm_fit_and_save(fprt_formula, vc_formula=variance_components, re_formula='0', group='group',
                         data=et_measures, centre=True, name='fprt_mlm', family='mlm', save_path=save_path)


def mixedlm_fit_and_save(formula, vc_formula, re_formula, group, data, centre, name, family, save_path):
    if centre:
        fixed_effects = get_continuous_fixed_effects(formula)
        data = centre_attributes(data, fixed_effects)
    if family == 'binomial':
        mixedlm_model = sm.BinomialBayesMixedGLM.from_formula(formula, vc_formulas=vc_formula, data=data)
        mixedlm_results = mixedlm_model.fit_vb()
    else:
        mixedlm_model = sm.MixedLM.from_formula(formula, groups=group, vc_formula=vc_formula, re_formula=re_formula,
                                                data=data)
        mixedlm_results = mixedlm_model.fit()
    print(mixedlm_results.summary())
    with open(save_path / name, 'w') as f:
        f.write(mixedlm_results.summary().as_text())


def count_by_skill(et_measures, measure):
    group_measure = et_measures.groupby(['reading_skill', 'item'])[measure].sum().reset_index()
    subjs_per_item = et_measures.groupby(['reading_skill', 'item'])['subj'].nunique().reset_index()
    group_measure[measure] = group_measure[measure] / subjs_per_item['subj']

    return group_measure


def get_continuous_fixed_effects(formula):
    fixed_effects = formula.split('~')[1].split('+')
    fixed_effects = [effect.strip() for effect in fixed_effects if 'C' not in effect]
    return fixed_effects


def centre_attributes(data, attributes):
    for attribute in attributes:
        data[attribute] = data[attribute] - data[attribute].mean()
    return data


def remove_skipped_words(et_measures):
    et_measures = et_measures[et_measures['skipped'] == 0]
    et_measures = et_measures.drop(columns=['skipped'])
    return et_measures


def remove_excluded_words(et_measures):
    et_measures = et_measures[~et_measures['excluded']]
    et_measures = et_measures.drop(columns=['excluded'])
    return et_measures


def add_len_freq_skipped(et_measures, words_freq):
    et_measures['skipped'] = et_measures[~et_measures['excluded']]['FFD'].apply(lambda x: int(x == 0))
    et_measures['word_len'] = et_measures['word'].apply(lambda x: len(x))
    words_freq['cnt'] = pd.qcut(words_freq['cnt'], 15, labels=[i for i in range(1, 16)])
    et_measures['word_freq'] = et_measures['word'].apply(lambda x:
                                                         words_freq.loc[words_freq['word'] == x, 'cnt'].values[0]
                                                         if x in words_freq['word'].values else 0)

    return et_measures


def log_normalize_durations(trial_measures):
    for duration_measure in ['FFD', 'SFD', 'FPRT', 'RPD', 'TFD', 'SPRT']:
        trial_measures[duration_measure] = trial_measures[duration_measure].apply(lambda x: log(x))

    return trial_measures


def plot_ffd_histogram(et_measures_no_skipped):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(x='FFD', data=et_measures_no_skipped, ax=ax, bins=50)
    ax.set_title('First Fixation Duration')
    ax.set_ylabel('Number of fixations')
    plt.show()
    plt.savefig(save_path / 'ffd_histogram.png')


def plot_aggregated_measures(et_measures, save_path):
    # Plot measures computed across trials (i.e., rates)
    aggregated_measures = et_measures.drop_duplicates(subset=['item', 'word_idx'])
    plot_boxplots('word_len', measures=['LS', 'RR'], data=aggregated_measures,
                  x_label='Word length', ax_titles=['Likelihood of skipping', 'Regression rate'], x_order='descending',
                  fig_title='Word length on rates', save_path=save_path / 'wordlen_on_rates.png')
    plot_boxplots('word_freq', measures=['LS', 'RR'], data=aggregated_measures,
                  x_label='Word frequency', ax_titles=['Likelihood of skipping', 'Regression rate'],
                  fig_title='Word frequency on rates', save_path=save_path / 'wordfreq_on_rates.png')


def plot_early_effects(et_measures, save_path):
    plot_boxplots('word_len', measures=['FFD', 'FPRT'], data=et_measures,
                  x_label='Word length', ax_titles=['First Fixation Duration', 'Gaze Duration'], x_order='descending',
                  fig_title='Early effects of word length', save_path=save_path / 'wordlen_effects.png')
    plot_boxplots('word_freq', measures=['FFD', 'FPRT'], data=et_measures,
                    x_label='Word frequency', ax_titles=['First Fixation Duration', 'Gaze Duration'],
                    fig_title='Early effects of word frequency', save_path=save_path / 'wordfreq_effects.png')


def plot_boxplots(fixed_effect, measures, data, x_label, ax_titles, x_order='ascending', fig_title=None, save_path=None):
    fig, axes = plt.subplots(1, len(measures), sharey='all', figsize=(12, 5))
    ax_titles = np.array(ax_titles)
    axes = [axes] if len(measures) == 1 else axes
    if x_order == 'descending':
        plot_order = sorted(data[fixed_effect].unique(), reverse=True)
    else:
        plot_order = sorted(data[fixed_effect].unique())
    for i, measure in enumerate(measures):
        sns.boxplot(x=fixed_effect, y=measure, data=data, ax=axes[i], order=plot_order)
        axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=15)
        axes[i].set_xlabel(x_label)
        axes[i].set_title(ax_titles[i])
    if fig_title:
        fig.suptitle(fig_title)
    if save_path:
        fig.savefig(save_path)
    plt.show()

    return fig


def load_trial(trial, item_name, words_freq, subjs_reading_skills):
    trial_measures = add_len_freq_skipped(pd.read_pickle(trial), words_freq)
    trial_measures.insert(1, 'reading_skill', subjs_reading_skills[trial_measures['subj'].iloc[0]])
    trial_measures.insert(0, 'item', item_name)
    return trial_measures


def load_trials_measures(item, words_freq, subjs_reading_skills):
    trials_measures = [load_trial(trial, item.name, words_freq, subjs_reading_skills) for trial in get_files(item)]
    return pd.concat(trials_measures, ignore_index=True)


def load_et_measures(items_paths, words_freq, subjs_reading_skills):
    measures = [load_trials_measures(item, words_freq, subjs_reading_skills) for item in items_paths]
    measures = pd.concat(measures, ignore_index=True)

    return measures


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Perform data analysis on extracted measures')
    parser.add_argument('--data_path', type=str, default='Data/processed/measures',
                        help='Path where eye-tracking measures are stored')
    parser.add_argument('--subjs_path', type=str, default='Data/processed/trials',
                        help='Path to participants\' trials, where their metadata is stored')
    parser.add_argument('--words_freq', type=str, default='Metadata/Texts_properties/words_freq.csv',
                        help='Path to file with words frequencies')
    parser.add_argument('--stats_file', type=str, default='Data/processed/words_fixations/stats.csv')
    parser.add_argument('--save_path', type=str, default='Results')
    parser.add_argument('--item', type=str, default='all')
    args = parser.parse_args()

    data_path, subjs_path, words_freq_file, stats_file, save_path = \
        Path(args.data_path), Path(args.subjs_path), Path(args.words_freq), Path(args.stats_file), Path(args.save_path)
    subjs_reading_skills = {subj.name: load_profile(subj)['reading_level'].iloc[0]
                            for subj in get_dirs(subjs_path)}

    if args.item != 'all':
        items_paths = [data_path / args.item]
    else:
        items_paths = get_dirs(data_path)

    do_analysis(items_paths, words_freq_file, stats_file, subjs_reading_skills, save_path)
