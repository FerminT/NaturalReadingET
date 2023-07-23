import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
import argparse
from pathlib import Path
from Code.data_processing.utils import get_dirs, get_files, log

""" Script to perform analysis on the extracted eye-tracking measures. """


def do_analysis(items_paths, subjs_paths, words_freq_path, stats_file, save_path):
    words_freq, items_stats = pd.read_csv(words_freq_path), pd.read_csv(stats_file, index_col=0)
    et_measures = load_et_measures(items_paths, words_freq)
    save_path.mkdir(parents=True, exist_ok=True)

    print_stats(et_measures, items_stats, save_path)
    et_measures = remove_excluded_words(et_measures)
    mlm_analysis(et_measures)
    et_measures = remove_skipped_words(et_measures)
    plot_early_effects(et_measures, save_path)


def print_stats(et_measures, items_stats, save_path):
    items = items_stats.index.to_list()[:-1]
    processed_stats = {item: {'subjs': 0, 'words': 0, 'words_excluded': 0, 'fix': 0, 'fix_excluded': 0,
                              'regressions': 0, 'skips': 0, 'out_of_bounds': 0, 'return_sweeps': 0}
                       for item in items}
    for item in items:
        item_measures = et_measures[et_measures['item'] == item]
        n_subjs = len(item_measures['subj'].unique())
        processed_stats[item]['subjs'] = n_subjs
        processed_stats[item]['words'] = len(item_measures[~item_measures['excluded']]['word']) // n_subjs
        processed_stats[item]['words_excluded'] = item_measures['excluded'].sum() // n_subjs
        processed_stats[item]['fix'] = item_measures['FC'].sum()
        processed_stats[item]['fix_excluded'] = items_stats.loc[item, 'n_fix'] - processed_stats[item]['fix']
        processed_stats[item]['regressions'] = item_measures['RC'].sum()
        processed_stats[item]['skipped'] = item_measures['skipped'].sum()
        processed_stats[item]['out_of_bounds'] = items_stats.loc[item, 'out_of_bounds']
        processed_stats[item]['return_sweeps'] = items_stats.loc[item, 'return_sweeps']

    processed_stats = pd.DataFrame.from_dict(processed_stats, orient='index', dtype='Int64')
    processed_stats.loc['Total'] = processed_stats.sum()
    print(processed_stats.to_string())

    processed_stats.to_csv(save_path / 'trials_stats.csv')


def mlm_analysis(et_measures):
    # This is a crossed random intercept (NOT slope) model with no independent groups
    et_measures['group'] = 1
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
    et_measures['word_len'] = et_measures['word'].apply(lambda x: 1 / len(x) if x else 0)
    et_measures['word_freq'] = et_measures['word'].apply(lambda x:
                                                         log(words_freq.loc[words_freq['word'] == x, 'cnt'].values[0])
                                                         if x in words_freq['word'].values else 0)
    return et_measures


def log_normalize_durations(trial_measures):
    for duration_measure in ['FFD', 'SFD', 'FPRT', 'RPD', 'TFD', 'SPRT']:
        trial_measures[duration_measure] = trial_measures[duration_measure].apply(lambda x: log(x))

    return trial_measures


def plot_boxplots(fixed_effect, measures, data, x_order='ascending'):
    fig, axes = plt.subplots(1, len(measures), sharey='all', figsize=(12, 5))
    if x_order == 'descending':
        plot_order = sorted(data[fixed_effect].unique(), reverse=True)
    else:
        plot_order = sorted(data[fixed_effect].unique())
    for i, measure in enumerate(measures):
        sns.boxplot(x=fixed_effect, y=measure, data=data, ax=axes[i], order=plot_order)
        axes[i].set_xticklabels(axes[i].get_xticklabels(), rotation=15)
        axes[i].set_title(f'{measure} effects')
    plt.show()

    return fig


def plot_early_effects(et_measures, save_path):
    et_measures['word_len'] = et_measures['word'].apply(lambda x: len(x))
    et_measures['word_freq'] = pd.qcut(et_measures['word_freq'], 15, labels=[i for i in range(1, 16)])
    wordlen_fig = plot_boxplots('word_len', measures=['FFD', 'FPRT'], data=et_measures, x_order='descending')
    wordfreq_fig = plot_boxplots('word_freq', measures=['FFD', 'FPRT'], data=et_measures)
    wordlen_fig.savefig(save_path / 'wordlen_effects.png')
    wordfreq_fig.savefig(save_path / 'wordfreq_effects.png')


def preprocess_data(trial_measures, words_freq):
    trial_measures = add_len_freq_skipped(trial_measures, words_freq)
    trial_measures = log_normalize_durations(trial_measures)

    return trial_measures


def load_trial(trial, item_name, words_freq):
    trial_measures = preprocess_data(pd.read_pickle(trial), words_freq)
    trial_measures.insert(1, 'item', item_name)
    return trial_measures


def load_trials_measures(item, words_freq):
    trials_measures = [load_trial(trial, item.name, words_freq) for trial in get_files(item)]
    return pd.concat(trials_measures, ignore_index=True)


def load_et_measures(items_paths, words_freq):
    measures = [load_trials_measures(item, words_freq) for item in items_paths]
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

    data_path, subjs_path, words_freq_path, stats_file, save_path = \
        Path(args.data_path), Path(args.subjs_path), Path(args.words_freq), Path(args.stats_file), Path(args.save_path)

    if args.item != 'all':
        items_paths = [data_path / args.item]
    else:
        items_paths = get_dirs(data_path)

    do_analysis(items_paths, subjs_path, words_freq_path, stats_file, save_path)
