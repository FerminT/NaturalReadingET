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
    et_measures = et_measures[~et_measures['skipped']]

    save_path.mkdir(parents=True, exist_ok=True)
    save_boxplots(et_measures, save_path)
    et_measures['group'] = 1
    vcf = {'subj': '0 + C(subj)', 'item': '0 + C(item)'}
    ffd_model = sm.MixedLM.from_formula('FFD ~ word_len', groups='group',
                                        vc_formula=vcf, re_formula='0', data=et_measures)
    ffd_results = ffd_model.fit()
    print(ffd_results.summary())


def preprocess_data(trial_measures, words_freq):
    """ Prepare the data for analysis. """
    trial_measures = trial_measures[~trial_measures['excluded']]
    trial_measures = trial_measures.drop(columns=['excluded'])
    trial_measures['skipped'] = trial_measures['FFD'] == 0
    trial_measures['word_len'] = trial_measures['word'].apply(lambda x: len(x))
    # Categorize frequency of words by deciles
    words_freq['cnt'] = pd.qcut(words_freq['cnt'], 10, labels=[i for i in range(1, 11)])
    trial_measures['word_freq'] = trial_measures['word'].apply(lambda x:
                                                               words_freq.loc[words_freq['word'] == x, 'cnt'].values[0])
    # Log normalize duration measures
    for duration_measure in ['FFD', 'SFD', 'FPRT', 'RPD', 'TFD', 'SPRT']:
        trial_measures[duration_measure] = trial_measures[duration_measure].apply(lambda x: np.log(x) if x > 0 else 0)

    return trial_measures


def plot_early_effects(fixed_effect, et_measures):
    fig, axes = plt.subplots(1, 2, sharey='all', figsize=(10, 5))
    sns.boxplot(x=fixed_effect, y='FFD', data=et_measures, ax=axes[0])
    sns.boxplot(x=fixed_effect, y='FPRT', data=et_measures, ax=axes[1])
    plt.show()

    return fig


def save_boxplots(et_measures, save_path):
    wordlen_fig = plot_early_effects('word_len', et_measures)
    wordfreq_fig = plot_early_effects('word_freq', et_measures)
    wordlen_fig.savefig(save_path / 'wordlen_effects.png')
    wordfreq_fig.savefig(save_path / 'wordfreq_effects.png')


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
