from parse_asc import ParseEyeLinkAsc
from pathlib import Path
import argparse

def parse_folder(datapath, location='asc'):
    participants = [dir_ for dir_ in datapath.iterdir() if dir_.is_dir()]
    for participant_dir in participants:
        asc_files = (participant_dir / location).glob('*.asc')
        for asc_file in asc_files:
            print(f'Processing {asc_file}')
            _, dfMsg, dfFix, dfSacc, _, _ = ParseEyeLinkAsc(asc_file)
            best_eye = find_besteye(dfMsg)
            dfFix, dfSacc = dfFix[dfFix['eye'] == best_eye], dfSacc[dfSacc['eye'] == best_eye]
            dfMsg = filter_msgs(dfMsg)

def find_besteye(dfMsg):
    val_msgs = (dfMsg[dfMsg['text'].str.contains('CAL VALIDATION')][-2:]).to_numpy(dtype=str)
    left_index  = int('LEFT' in val_msgs[1][1])
    right_index = 1 - left_index
    lefterror_index, righterror_index = val_msgs[left_index][1].split().index('ERROR'), val_msgs[right_index][1].split().index('ERROR')
    left_error  = float(val_msgs[left_index][1].split()[lefterror_index + 1])
    right_error = float(val_msgs[right_index][1].split()[righterror_index + 1])
    
    return 'L' if left_error < right_error else 'R'

def filter_msgs(dfMsg, cutout='validation'):
    first_index = dfMsg.index[dfMsg['text'].str.contains('validation')].tolist()[0]
    
    return dfMsg[first_index:]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract fixations from EyeLink .asc file')
    parser.add_argument('-path', type=str, help='Path where participants data is stored')
    args = parser.parse_args()

    datapath = Path(args.path)
    parse_folder(datapath)