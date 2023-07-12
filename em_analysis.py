import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import statsmodels.api as sm
import argparse
from pathlib import Path
from Code.data_processing import utils

""" Script to perform analysis on the extracted eye-tracking measures. """


def do_analysis(items_paths, subjs_paths, words_freq_path, save_path):
    words_freq = pd.read_csv(words_freq_path)
    et_measures = load_et_measures(items_paths, words_freq)
    save_path.mkdir(parents=True, exist_ok=True)

    mlm_analysis(et_measures)
    et_measures = remove_skipped_words(et_measures)
    plot_early_effects(et_measures, save_path)


def mlm_analysis(et_measures):
    # This is a crossed random intercept (NOT slope) model with no independent groups
    et_measures['group'] = 1
    variance_components = {'subj': '0 + C(subj)', 'item': '0 + C(item)'}
    skipped_formula = 'skipped ~ word_len'
    mixedlm_fit_and_save(skipped_formula, vc_formula=variance_components, re_formula='0', group='group',
                         data=et_measures, model_name='skipped_mlm', model_type='binomial', save_path=save_path)
    et_measures = remove_skipped_words(et_measures)
    ffd_formula = 'FFD ~ word_len + word_freq'
    fprt_formula = 'FPRT ~ word_len + word_freq'
    mixedlm_fit_and_save(ffd_formula, vc_formula=variance_components, re_formula='0', group='group',
                         data=et_measures, model_name='ffd_mlm', model_type='mlm', save_path=save_path)
    mixedlm_fit_and_save(fprt_formula, vc_formula=variance_components, re_formula='0', group='group',
                         data=et_measures, model_name='fprt_mlm', model_type='mlm', save_path=save_path)


def mixedlm_fit_and_save(formula, vc_formula, re_formula, group, data, model_name, model_type, save_path):
    if model_type == 'binomial':
        mixedlm_model = sm.GLM.from_formula(formula, groups=group, vc_formula=vc_formula, re_formula=re_formula,
                                            data=data, family=sm.families.Binomial())
    else:
        mixedlm_model = sm.MixedLM.from_formula(formula, groups=group, vc_formula=vc_formula, re_formula=re_formula,
                                                data=data)
    mixedlm_results = mixedlm_model.fit()
    print(mixedlm_results.summary())
    with open(save_path / model_name, 'w') as f:
        f.write(mixedlm_results.summary().as_text())


def remove_skipped_words(et_measures):
    et_measures = et_measures[~et_measures['skipped']]
    et_measures = et_measures.drop(columns=['skipped'])
    return et_measures


def remove_excluded_words(et_measures):
    et_measures = et_measures[~et_measures['excluded']]
    et_measures = et_measures.drop(columns=['excluded'])
    return et_measures


def add_len_freq_skipped(et_measures, words_freq):
    et_measures['skipped'] = et_measures['FFD'].apply(lambda x: x == 0)
    et_measures['word_len'] = et_measures['word'].apply(lambda x: len(x))
    # Categorize frequency of words by deciles
    words_freq['cnt'] = pd.qcut(words_freq['cnt'], 10, labels=[i for i in range(1, 11)])
    et_measures['word_freq'] = et_measures['word'].apply(lambda x:
                                                         words_freq.loc[words_freq['word'] == x, 'cnt'].values[0])
    return et_measures


def log_normalize_durations(trial_measures):
    for duration_measure in ['FFD', 'SFD', 'FPRT', 'RPD', 'TFD', 'SPRT']:
        trial_measures[duration_measure] = trial_measures[duration_measure].apply(lambda x: np.log(x) if x > 0 else 0)

    return trial_measures


def plot_boxplots(fixed_effect, measures, data):
    fig, axes = plt.subplots(1, len(measures), sharey='all', figsize=(10, 5))
    for i, measure in enumerate(measures):
        sns.boxplot(x=fixed_effect, y=measure, data=data, ax=axes[i])
    plt.show()

    return fig


def plot_early_effects(et_measures, save_path):
    wordlen_fig = plot_boxplots('word_len', measures=['FFD', 'FPRT'], data=et_measures)
    wordfreq_fig = plot_boxplots('word_freq', measures=['FFD', 'FPRT'], data=et_measures)
    wordlen_fig.savefig(save_path / 'wordlen_effects.png')
    wordfreq_fig.savefig(save_path / 'wordfreq_effects.png')


def preprocess_data(trial_measures, words_freq):
    trial_measures = remove_excluded_words(trial_measures)
    trial_measures = add_len_freq_skipped(trial_measures, words_freq)
    trial_measures = log_normalize_durations(trial_measures)

    return trial_measures


def load_trial(trial, item_name, words_freq):
    trial_measures = preprocess_data(pd.read_pickle(trial), words_freq)
    trial_measures.insert(1, 'item', item_name)
    return trial_measures


def load_trials_measures(item, words_freq):
    trials_measures = [load_trial(trial, item.name, words_freq) for trial in utils.get_files(item)]
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
    parser.add_argument('--save_path', type=str, default='Results')
    parser.add_argument('--item', type=str, default='all')
    args = parser.parse_args()

    data_path, subjs_path, words_freq_path, save_path = \
        Path(args.data_path), Path(args.subjs_path), Path(args.words_freq), Path(args.save_path)

    if args.item != 'all':
        items_paths = [data_path / args.item]
    else:
        items_paths = utils.get_dirs(data_path)

    do_analysis(items_paths, subjs_path, words_freq_path, save_path)
