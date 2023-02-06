import numpy as np
import pandas as pd
import time
from pathlib import Path

def ParseEyeLinkAsc(elFilename):
    """Reads in .asc data files from EyeLink and produces pandas dataframes for further analysis
    
    Created 7/31/18-8/15/18 by DJ.
    Updated 7/4/19 by DJ - detects and handles monocular sample data.
    dfRec,dfMsg,dfFix,dfSacc,dfBlink,dfSamples = ParseEyeLinkAsc(elFilename)
    -Reads in data files from EyeLink .asc file and produces readable dataframes for further analysis.
    
    INPUTS:
    -elFilename is a string indicating an EyeLink data file from an AX-CPT task in the current path.
    
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
    print('Parsing EyeLink ASCII file %s...'%str(elFilename))
    t0 = time.time()
    with elFilename.open('r') as fp:
        fileTxt0 = fp.read().splitlines(keeplinebreaks=True)
        
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
    dfRecStart = pd.read_csv(elFilename, skiprows=iNotStart, header=None, delim_whitespace=True, usecols=[1], low_memory=False)
    dfRecStart.columns = ['tStart']
    iNotEnd = np.nonzero(lineType!='END')[0]
    dfRecEnd = pd.read_csv(elFilename, skiprows=iNotEnd, header=None, delim_whitespace=True, usecols=[1,5,6], low_memory=False)
    dfRecEnd.columns = ['tEnd', 'xRes', 'yRes']
    # combine trial info
    dfRec = pd.concat([dfRecStart, dfRecEnd],axis=1)
    nRec = dfRec.shape[0]
    print('%d recording periods found.'%nRec)

    
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
    print(f'{len(iMsg)} messages')
    
    # Import Fixations
    iNotEfix = np.nonzero(lineType!='EFIX')[0]
    dfFix = pd.read_csv(elFilename, skiprows=iNotEfix, header=None, delim_whitespace=True, usecols=range(1,8), low_memory=False)
    dfFix.columns = ['eye', 'tStart', 'tEnd', 'duration', 'xAvg', 'yAvg', 'pupilAvg']
    nFix = dfFix.shape[0]
    print(f'{nFix} fixations')

    # Saccades
    iNotEsacc = np.nonzero(lineType!='ESACC')[0]
    dfSacc = pd.read_csv(elFilename, skiprows=iNotEsacc, header=None, delim_whitespace=True, usecols=range(1,11), low_memory=False)
    dfSacc.columns = ['eye', 'tStart', 'tEnd', 'duration', 'xStart', 'yStart', 'xEnd', 'yEnd', 'ampDeg', 'vPeak']
    print(f'{dfSacc.shape[0]} saccades')
    
    # Blinks
    dfBlink = pd.DataFrame()
    iNotEblink = np.nonzero(lineType!='EBLINK')[0]
    if len(iNotEblink) < nLines:
      dfBlink = pd.read_csv(elFilename, skiprows=iNotEblink, header=None, delim_whitespace=True, usecols=range(1,5), low_memory=False)
      dfBlink.columns = ['eye', 'tStart', 'tEnd', 'duration']
      print(f'{dfBlink.shape[0]} blinks')
      
    # determine sample columns based on eyes recorded in file
    eyesInFile = np.unique(dfFix.eye)
    if eyesInFile.size == 2:
        print('binocular data detected.')
        cols = ['tSample', 'LX', 'LY', 'LPupil', 'RX', 'RY', 'RPupil']
    else:
        eye = eyesInFile[0]
        print('monocular data detected (%c eye).'%eye)
        cols = ['tSample', '%cX'%eye, '%cY'%eye, '%cPupil'%eye]
        
    # Import samples    
    iNotSample = np.nonzero(np.logical_or(lineType!='SAMPLE', np.arange(nLines) < iStartRec))[0]
    dfSamples = pd.read_csv(elFilename, skiprows=iNotSample, header=None, delim_whitespace=True, usecols=range(0, len(cols)), low_memory=False)
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
            
    print(f'{dfSamples.shape[0]} samples')
    print('Done! Took %.1f seconds.'%(time.time()-t0))
    
    return dfRec, dfMsg, dfFix, dfSacc, dfBlink, dfSamples