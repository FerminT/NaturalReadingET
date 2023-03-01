from pathlib import Path
from Code.data_processing import parse_trials
import argparse

def select_trial(raw_path, ascii_path, config, stimuli_path, data_path, subj):
    subj_datapath = Path(data_path) / subj
    subj_rawpath  = Path(raw_path) / subj
    if not subj_rawpath.exists():
        raise ValueError('Participant not found')
    subj_rawitems = [item.name[:-4] for item in subj_rawpath.glob('*.mat') if not item.name in ['Test.mat', 'metadata.mat']]
    if subj_datapath.exists():
        subj_processeditems = [item.name for item in subj_datapath.iterdir() if item.is_dir()]
        missing_items = [item for item in subj_rawitems if item not in subj_processeditems]
    else:
        missing_items = subj_rawitems
        parse_trials.save_profile(subj_rawpath, subj_datapath)
    for rawitem in missing_items:
        parse_trials.parse_item(subj_rawpath / f'{rawitem}.mat', subj_rawpath, ascii_path, config, Path(stimuli_path), subj_datapath)
        
    print('Available items:')
    for i in range(len(subj_rawitems)):
        print(f"{i+1}. {subj_rawitems[i]}")
    choice = input('Enter the item number to edit: ')
    while not choice.isdigit() or int(choice) < 1 or int(choice) > len(subj_rawitems):
        print('Invalid choice. Please enter a number between 1 and', len(subj_rawitems))
        choice = input('Enter the item number to edit: ')

    print('You selected:', subj_rawitems[int(choice)-1])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Edit a trial from a given participant')
    parser.add_argument('--raw', type=str, default='Data/raw', help='Path where participants raw data is stored in ASCII format')
    parser.add_argument('--ascii_path', type=str, default='asc', help='Path where .asc files are stored in a participants folder')
    parser.add_argument('--config', type=str, default='Metadata/stimuli_config.mat', help='Config file with the stimuli information')
    parser.add_argument('--stimuli_path', type=str, default='Stimuli', help='Path where the stimuli are stored')
    parser.add_argument('--data', type=str, default='Data/processed/by_participant', help='Path where the processed data is stored in pkl format')
    parser.add_argument('--subj', type=str, help='Participant\'s name', required=True)
    args = parser.parse_args()
    
    select_trial(args.raw, args.ascii_path, args.config, args.stimuli_path, args.data, args.subj)