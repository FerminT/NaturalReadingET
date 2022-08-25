function [edfFile]=eyelink_ini(filename);

% Esta es la funcion que hay que llamar para que inicialize el eyelink,
% poner antes del programa que querramos correr en  matlab. Queda grabando
% y se cierra la screen.

% si no le pongo nombre de archivo me pone test.edf por default.
if ~exist('filename','var')
    filename='test';
    disp('Usando filename default: test')
end

if 1 Screen('Preference', 'SkipSyncTests', 1); end

    fprintf('EyelinkToolbox Example\n\n\t');

    % STEP 1
    % Initialization of the connection with the Eyelink Gazetracker.
    % exit program if this fails.
    
    if EyelinkInit()~= 1; %
    	return;
    end;
    % STEP 2
    % Open a graphics window on the main screen
    % using the PsychToolbox's Screen function.

    screenNumber=max(Screen('Screens'));
    [window, wRect]=Screen('OpenWindow', screenNumber, 0,[],32,2);
    Screen(window,'BlendFunction',GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    
    % STEP 3
    % Provide Eyelink with details about the graphics environment
    % and perform some initializations. The information is returned
    % in a structure that also contains useful defaults
    % and control codes (e.g. tracker state bit and Eyelink key values).
    el=EyelinkInitDefaults(window);

    % make sure that we get gaze data from the Eyelink
    Eyelink('Command', 'link_sample_data = LEFT,RIGHT,GAZE,AREA');



    % open file to record data to
    edfFile=filename;
    Eyelink('Openfile', edfFile);

    % STEP 4
    % Calibrate the eye tracker
    EyelinkDoTrackerSetup(el);

    % do a final check of calibration using driftcorrection
    EyelinkDoDriftCorrection(el);

    % STEP 5
    % start recording eye position
    Eyelink('StartRecording');
    % record a few samples before we actually start displaying
    WaitSecs(0.1);
    % mark zero-plot time in data file
    Eyelink('Message', 'SYNCTIME');
    stopkey=KbName('space');
    eye_used = -1;
    Screen('CloseAll');
