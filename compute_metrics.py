from Code.data_processing import utils
from pathlib import Path
import argparse

WEIRD_CHARS = ['¿', '?', '¡', '!', '“', '”', '.']  # Excluded '(', ')' and ',', ';', ':', '—', '«', '»'
CHARS_MAP = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
             'Á': 'A', 'É': 'E', 'I': 'I', 'Ó': 'O', 'Ú': 'U',
             '(': '', ')': '', ';': '', ',': '', ':': ''}


def compute_metrics(items, save_file, chars_mapping):
    metrics_by_word = {}
    for item in items:
        screens_text = utils.load_json(item, 'screens_text.json')
        for screenid in screens_text:
            screen_text = screens_text[screenid]
            screen_path = item / f'screen_{screenid}'
            trials = utils.get_dirs(screen_path)
            for trial in trials:
                for num_line, line in enumerate(screen_text):
                    line_fixations = utils.load_json(trial, f'line_{num_line + 1}.json')
                    line_words = line.split()
                    for word_pos, word in enumerate(line_words):
                        word_fixations = line_fixations[word_pos]
                        is_first_word, is_last_word = word_pos == 0, word_pos == len(line_words) - 1
                        has_weird_chars = any(char in word for char in WEIRD_CHARS)
                        if len(word_fixations) == 0 or has_weird_chars or is_first_word or is_last_word:
                            continue
                        word = word.lower().translate(chars_mapping)
                        fixation_counter = 0
                        for fixation in word_fixations['index']:
                            # Count consecutive fixations on the word
                            # This discards inter-word regressions, but counts intra-word regressions
                            if fixation_counter == 0:
                                prev_fix = fixation
                            elif fixation != prev_fix + 1:
                                break
                            fixation_counter += 1
                        if word not in metrics_by_word:
                            metrics_by_word[word] = fixation_counter
                        else:
                            metrics_by_word[word] += fixation_counter
    utils.save_json(metrics_by_word, save_file.parent, save_file.name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compute metrics based on words fixations')
    parser.add_argument('--data_path', type=str, default='Data/processed/by_item')
    parser.add_argument('--save_file', type=str, default='Data/processed/metrics.json')
    parser.add_argument('--item', type=str, default='all')
    args = parser.parse_args()

    data_path, save_file = Path(args.data_path), Path(args.save_file)
    if args.item != 'all':
        item_paths = [data_path / args.item]
    else:
        item_paths = utils.get_dirs(data_path)

    chars_mapping = str.maketrans(CHARS_MAP)
    compute_metrics(item_paths, save_file, chars_mapping)
