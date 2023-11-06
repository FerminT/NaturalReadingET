import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
import argparse
from pathlib import Path
from scripts.data_processing.extract_measures import main as extract_measures
from scripts.data_processing.wa_task import parse_wa_task
from scripts.data_processing.utils import get_dirs, get_files, log, load_profile

""" Script to perform data analysis on eye-tracking measures. It is composed of three steps:
    1. Assign the fixations from each trial to their corresponding word in the text
    2. Extract measures from fixations (FFD, FPRT, RPD, TFD, FC, etc.)
    3. Perform data analysis on the extracted measures """


def do_analysis(items_paths, words_freq_file, stats_file, subjs_reading_skills, save_path):
    print('Analysing eye-tracking measures...')
    words_freq, items_stats = pd.read_csv(words_freq_file), pd.read_csv(stats_file, index_col=0)
    et_measures = load_et_measures(items_paths, words_freq, subjs_reading_skills)
    print_stats(et_measures, items_stats, save_path)

    et_measures = remove_excluded_words(et_measures)
    plot_measures(et_measures, save_path)
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


def plot_measures(et_measures, save_path):
    plot_skills_effects(et_measures, save_path)
    et_measures_no_skipped = remove_skipped_words(et_measures)
    plot_histograms(et_measures_no_skipped, ['FFD', 'FC'], ax_titles=['First Fixation Duration', 'Fixation Count'],
                    y_labels=['Number of words', 'Number of words'], save_file=save_path / 'FFD_FC_distributions.png')
    plot_words_effects(et_measures, save_path)


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


def categorize_skill(reading_skill, thresholds):
    category = 'low'
    if thresholds['low'] < reading_skill <= thresholds['medium']:
        category = 'medium'
    elif reading_skill > thresholds['medium']:
        category = 'high'

    return category


def plot_skills_effects(et_measures, save_path):
    skills_threshold = {'low': 6, 'medium': 9, 'high': 10}
    et_measures['reading_skill'] = et_measures['reading_skill'].apply(lambda x: categorize_skill(x, skills_threshold))
    et_measures_no_skipped = log_normalize_durations(remove_skipped_words(et_measures))

    skip_count = count_by_skill(et_measures, 'skipped')
    fix_count = count_by_skill(et_measures_no_skipped, 'FC')
    regression_count = count_by_skill(et_measures_no_skipped, 'RC')

    y_labels = ['log First Fixation Duration', 'log Gaze Duration', 'Mean fixation count', 'Mean regression count',
                'Mean number of skips']
    plot_boxplots(['reading_skill'], measures=['FFD', 'FPRT', 'FC', 'RC', 'skipped'],
                  data=[et_measures_no_skipped, et_measures_no_skipped, fix_count, regression_count, skip_count],
                  x_labels=['Reading skill'] * 5,
                  y_labels=y_labels,
                  ax_titles=y_labels,
                  fig_title='Reading skill on eye-tracking measures',
                  save_file=save_path / 'skills_on_measures.png',
                  sharey=False,
                  orientation='vertical',
                  order=['low', 'medium', 'high'])


def plot_words_effects(et_measures, save_path):
    et_measures_log = log_normalize_durations(remove_skipped_words(et_measures))
    aggregated_measures = et_measures.drop_duplicates(subset=['item', 'word_idx'])
    y_labels = ['log First Fixation Duration', 'log Gaze Duration', 'Likelihood of skipping', 'Regression rate']
    plot_boxplots(['word_len'], measures=['FFD', 'FPRT', 'LS', 'RR'],
                  data=[et_measures_log, et_measures_log, aggregated_measures, aggregated_measures],
                  x_labels=['Word length'] * 4,
                  y_labels=y_labels,
                  ax_titles=y_labels,
                  fig_title='Word length effects on measures',
                  save_file=save_path / 'word_length.png')

    plot_boxplots(['word_freq'], measures=['FFD', 'FPRT', 'LS', 'RR'],
                  data=[et_measures_log, et_measures_log, aggregated_measures, aggregated_measures],
                  x_labels=['Word frequency in percentiles'] * 4,
                  y_labels=y_labels,
                  ax_titles=y_labels,
                  fig_title='Word frequency effects on measures',
                  save_file=save_path / 'word_frequency.png')


def plot_boxplots(fixed_effects, measures, data, x_labels, y_labels, ax_titles,
                  fig_title, save_file, sharey='row', orientation='horizontal', order=None):
    n_plots = len(fixed_effects) * len(measures)
    n_cols = int(np.ceil(np.sqrt(n_plots)))
    n_rows = int(np.ceil(n_plots / n_cols))
    if orientation == 'vertical':
        n_cols, n_rows = n_rows, n_cols
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, sharey=sharey, figsize=(n_cols * 7, n_rows * 6))
    axes = [axes] if n_plots == 1 else axes
    for i, fixed_effect in enumerate(fixed_effects):
        for j, measure in enumerate(measures):
            ax = axes[(i + j) // n_cols, (i + j) % n_cols]
            plot_data = data[j] if isinstance(data, list) else data
            sns.boxplot(x=fixed_effect, y=measure, data=plot_data, order=order, ax=ax)
            ax.set_xticklabels(ax.get_xticklabels(), rotation=15)
            ax.yaxis.set_tick_params(labelleft=True)
            ax.set_xlabel(x_labels[i])
            ax.set_ylabel(y_labels[j])
            ax.set_title(ax_titles[j])
    fig.suptitle(fig_title)
    fig.savefig(save_file, bbox_inches='tight')
    plt.show()

    return fig


def plot_histograms(et_measures, measures, ax_titles, y_labels, save_file):
    ncols = len(measures) // 2
    nrows = 2 if len(measures) > 1 else 1
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols)
    axes = np.array(axes)[:, np.newaxis] if len(measures) <= 2 else axes
    for i, measure in enumerate(measures):
        ax = axes[i // ncols, i % ncols]
        sns.histplot(x=measure, data=et_measures, ax=ax, binwidth=1)
        ax.set_title(ax_titles[i])
        ax.set_ylabel(y_labels[i])
    plt.tight_layout()
    plt.show()
    fig.savefig(save_file)


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
    parser = argparse.ArgumentParser(description='Perform data analysis on extracted eye-tracking measures')
    parser.add_argument('-w', '--wordsfix', type=str, default='data/processed/words_fixations',
                        help='Where items\' fixations by word are stored')
    parser.add_argument('-m', '--measures', type=str, default='results/measures',
                        help='Path where eye-tracking measures are stored')
    parser.add_argument('-s', '--stimuli', type=str, default='stimuli',
                        help='Items path, from which the stimuli (items\' text) is extracted')
    parser.add_argument('-p', '--participants', type=str, default='data/processed/trials',
                        help='Path to participants\' trials, where their fixations and metadata are stored.')
    parser.add_argument('-q', '--questions', type=str, default='metadata/stimuli_questions.mat',
                        help='Path to file with items\' questions')
    parser.add_argument('-wf', '--words_freq', type=str, default='metadata/texts_properties/words_freq.csv',
                        help='Path to file with words frequencies')
    parser.add_argument('-st', '--stats', type=str, default='data/processed/words_fixations/stats.csv')
    parser.add_argument('-o', '--output', type=str, default='results')
    parser.add_argument('-i', '--item', type=str, default='all')
    args = parser.parse_args()

    wordsfix_path, measures_path, stimuli_path, participants_path, save_path = \
        Path(args.wordsfix), Path(args.measures), Path(args.stimuli), Path(args.participants), Path(args.output)
    words_freq_file, stats_file, questions_file = Path(args.words_freq), Path(args.stats), Path(args.questions)
    subjs_reading_skills = {subj.name: load_profile(subj)['reading_level'].iloc[0]
                            for subj in get_dirs(participants_path)}
    subjects_associations, words_associations = parse_wa_task(questions_file, participants_path)

    extract_measures(args.item, wordsfix_path, stimuli_path, participants_path, save_path, reprocess=False)

    if args.item != 'all':
        items_paths = [measures_path / args.item]
    else:
        items_paths = get_dirs(measures_path)

    save_path.mkdir(parents=True, exist_ok=True)
    subjects_associations.to_csv(save_path / 'subjects_associations.csv')
    words_associations.to_csv(save_path / 'words_associations.csv')

    do_analysis(items_paths, words_freq_file, stats_file, subjs_reading_skills, save_path)
