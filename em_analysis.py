import pandas as pd
import argparse
from pathlib import Path
from Code.data_processing import utils

""" Script to perform analysis on the extracted eye-tracking measures. """


def do_analysis(items_paths, subjs_paths, save_path):
    et_measures = load_et_measures(items_paths)


def load_trial(trial, item_name):
    trial_measures = pd.read_pickle(trial)
    trial_measures.insert(1, 'item', item_name)
    return trial_measures


def load_trials_measures(item):
    trials_measures = [load_trial(trial, item.name) for trial in utils.get_files(item)]
    return pd.concat(trials_measures, ignore_index=True)


def load_et_measures(items_paths):
    items_paths = items_paths[:2]
    measures = [load_trials_measures(item) for item in items_paths]
    measures = pd.concat(measures, ignore_index=True)

    return measures


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Perform data analysis on extracted measures')
    parser.add_argument('--data_path', type=str, default='Data/processed/measures',
                        help='Path where eye-tracking measures are stored')
    parser.add_argument('--subjs_path', type=str, default='Data/processed/trials',
                        help='Path to participants\' trials, where their metadata is stored')
    parser.add_argument('--save_path', type=str, default='Results')
    parser.add_argument('--item', type=str, default='all')
    args = parser.parse_args()

    data_path, subjs_path, save_path = Path(args.data_path), Path(args.subjs_path), Path(args.save_path)

    if args.item != 'all':
        items_paths = [data_path / args.item]
    else:
        items_paths = utils.get_dirs(data_path)

    do_analysis(items_paths, subjs_path, save_path)
