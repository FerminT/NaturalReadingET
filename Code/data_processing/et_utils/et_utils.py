import numpy as np
import pandas as pd
import time

def parse_asc(filename, verbose=True):
    """Reads in .asc data files from EyeLink and produces pandas dataframes for further analysis
    
    Created 7/31/18-8/15/18 by DJ.
    Updated 7/4/19 by DJ - detects and handles monocular sample data.
    dfRec,dfMsg,dfFix,dfSacc,dfBlink,dfSamples = ParseEyeLinkAsc(filename)
    -Reads in data files from EyeLink .asc file and produces readable dataframes for further analysis.
    
    INPUTS:
    -filename is a string indicating an EyeLink data file from an AX-CPT task in the current path.
    
    OUTPUTS:
    -dfRec contains information about recording periods (often trials)
    -dfMsg contains information about messages (usually sent from stimulus software)
    -dfFix contains information about fixations
    -dfSacc contains information about saccades
    -dfBlink contains information about blinks
    -dfSamples contains information about individual samples
    
    Created 7/31/18-8/15/18 by DJ.
    Updated 11/12/18 by DJ - switched from "trials" to "recording periods" for experiments with continuous recording
    Modified by Gustavo Juantorena (github.com/gej1) 06/01/22
    """
    if verbose:
        print('Parsing EyeLink ASCII file %s...'%str(filename))
    t0 = time.time()
    with filename.open('r') as fp:
        fileTxt0 = fp.read().splitlines(keepends=True)
        
    fileTxt0 = list(filter(None, fileTxt0))
    fileTxt0 = np.array(fileTxt0)

    # Separate lines into samples and messages
    nLines = len(fileTxt0)
    lineType  = np.array(['OTHER'] * nLines, dtype='object')
    iStartRec = None
    for iLine in range(nLines):
        if len(fileTxt0[iLine]) < 3:
            lineType[iLine] = 'EMPTY'
        elif fileTxt0[iLine].startswith('*') or fileTxt0[iLine].startswith('>>>>>'):
            lineType[iLine] = 'COMMENT'
        elif fileTxt0[iLine].split()[0][0].isdigit() or fileTxt0[iLine].split()[0].startswith('-'):
            lineType[iLine] = 'SAMPLE'
        else:
            lineType[iLine] = fileTxt0[iLine].split()[0]
        if '!CAL' in fileTxt0[iLine]:
            iStartRec = iLine + 1 
    
    # ===== PARSE EYELINK FILE ===== #
    iNotStart = np.nonzero(lineType!='START')[0]
    dfRecStart = pd.read_csv(filename, skiprows=iNotStart, header=None, delim_whitespace=True, usecols=[1], low_memory=False)
    dfRecStart.columns = ['tStart']
    iNotEnd = np.nonzero(lineType!='END')[0]
    dfRecEnd = pd.read_csv(filename, skiprows=iNotEnd, header=None, delim_whitespace=True, usecols=[1,5,6], low_memory=False)
    dfRecEnd.columns = ['tEnd', 'xRes', 'yRes']
    # combine trial info
    dfRec = pd.concat([dfRecStart, dfRecEnd],axis=1)
    nRec = dfRec.shape[0]
    
    # Import Messages
    t = time.time()
    iMsg = np.nonzero(lineType=='MSG')[0]
    tMsg = []
    txtMsg = []
    for i in range(len(iMsg)):
        # separate MSG prefix and timestamp from rest of message
        info = fileTxt0[iMsg[i]].split()
        # extract info
        tMsg.append(int(info[1]))
        txtMsg.append(' '.join(info[2:]))
    dfMsg = pd.DataFrame({'time': tMsg, 'text': txtMsg})
    
    # Import Fixations
    iNotEfix = np.nonzero(lineType!='EFIX')[0]
    dfFix = pd.read_csv(filename, skiprows=iNotEfix, header=None, delim_whitespace=True, usecols=range(1,8), low_memory=False)
    dfFix.columns = ['eye', 'tStart', 'tEnd', 'duration', 'xAvg', 'yAvg', 'pupilAvg']

    # Saccades
    iNotEsacc = np.nonzero(lineType!='ESACC')[0]
    dfSacc = pd.read_csv(filename, skiprows=iNotEsacc, header=None, delim_whitespace=True, usecols=range(1,11), low_memory=False)
    dfSacc.columns = ['eye', 'tStart', 'tEnd', 'duration', 'xStart', 'yStart', 'xEnd', 'yEnd', 'ampDeg', 'vPeak']
    
    # Blinks
    dfBlink = pd.DataFrame()
    iNotEblink = np.nonzero(lineType!='EBLINK')[0]
    if len(iNotEblink) < nLines:
      dfBlink = pd.read_csv(filename, skiprows=iNotEblink, header=None, delim_whitespace=True, usecols=range(1,5), low_memory=False)
      dfBlink.columns = ['eye', 'tStart', 'tEnd', 'duration']
      
    # determine sample columns based on eyes recorded in file
    eyesInFile = np.unique(dfFix.eye)
    if eyesInFile.size == 2:
        cols = ['tSample', 'LX', 'LY', 'LPupil', 'RX', 'RY', 'RPupil']
    else:
        eye = eyesInFile[0]
        print('monocular data detected (%c eye).'%eye)
        cols = ['tSample', '%cX'%eye, '%cY'%eye, '%cPupil'%eye]
        
    # Import samples    
    iNotSample = np.nonzero(np.logical_or(lineType!='SAMPLE', np.arange(nLines) < iStartRec))[0]
    dfSamples = pd.read_csv(filename, skiprows=iNotSample, header=None, delim_whitespace=True, usecols=range(0, len(cols)), low_memory=False)
    dfSamples.columns = cols
    # Convert values to numbers
    for eye in ['L', 'R']:
        if eye in eyesInFile:
            dfSamples['%cX'%eye] = pd.to_numeric(dfSamples['%cX'%eye],errors='coerce')
            dfSamples['%cY'%eye] = pd.to_numeric(dfSamples['%cY'%eye],errors='coerce')
            dfSamples['%cPupil'%eye] = pd.to_numeric(dfSamples['%cPupil'%eye],errors='coerce')
        else:
            dfSamples['%cX'%eye] = np.nan
            dfSamples['%cY'%eye] = np.nan
            dfSamples['%cPupil'%eye] = np.nan
    
    if verbose:
        print('%d recording periods found.'%nRec)
        print(f'{len(iMsg)} messages')
        print(f'{dfFix.shape[0]} fixations')
        print(f'{dfSacc.shape[0]} saccades')
        print(f'{dfBlink.shape[0]} blinks')
        print(f'{dfSamples.shape[0]} samples')
        if eyesInFile.size == 2:
            print('binocular data detected.')
        else:
            print('monocular data detected (%c eye).'%eyesInFile[0])
        print('Done! Took %.1f seconds.'%(time.time()-t0))
    
    return dfRec, dfMsg, dfFix, dfSacc, dfBlink, dfSamples

def find_besteye(dfMsg, default='R'):
    val_msgs = (dfMsg[dfMsg['text'].str.contains('CAL VALIDATION')][-2:]).to_numpy(dtype=str)
    if 'ABORTED' in val_msgs[0][1]: return default
    
    left_index  = int('LEFT' in val_msgs[1][1])
    right_index = 1 - left_index
    lefterror_index, righterror_index = val_msgs[left_index][1].split().index('ERROR'), val_msgs[right_index][1].split().index('ERROR')
    left_error  = float(val_msgs[left_index][1].split()[lefterror_index + 1])
    right_error = float(val_msgs[right_index][1].split()[righterror_index + 1])
    
    return 'L' if left_error < right_error else 'R'

def filter_msgs(dfMsg, cutout='validation'):
    first_index = dfMsg.index[dfMsg['text'].str.contains(cutout)].tolist()[0]
    
    return dfMsg[first_index:]

def is_binocular(dfFix):
    return len(dfFix['eye'].unique()) > 1

def keep_besteye(dfFix, dfMsg, default='R'):
    if is_binocular(dfFix):
        best_eye = find_besteye(dfMsg, default)
        dfFix = dfFix[dfFix['eye'] == best_eye]
    
    return dfFix