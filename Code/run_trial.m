function run_trial(subjname, numtrial, trial_order, constants, config)
    % addpath('C:\Documents and Settings\Diego\Mis documentos\Dropbox\_LABO\eyetracker_Funciones')
    
    Screen('Preference', 'SkipSyncTests', 1);
    Screen('Preference', 'VisualDebuglevel', 3); % remove presentation screen
    Screen('Preference', 'Verbosity', 1); % remove warnings
    
    USE_EYETRACKER = 0;
    
    CONFIG_FILE  = fullfile('..', 'stimuli_config.mat');
    STIMULI_PATH = fullfile('..', 'Stimuli');
    % SAVE_PATH    = fullfile('..', 'Data');
    
    files      = dir(STIMULI_PATH);
    filenames  = string({files([files.isdir] == 0).name});
    
    [idstimuli, ok] = listdlg('PromptString','Elija un texto a presentar:', ...
                    'SelectionMode','single', ...
                    'ListSize', [400 300], ...
                    'ListString', filenames);
    if ok == 0
        return
    end
    
    selected_stimuli = fullfile(STIMULI_PATH, filenames{idstimuli});            
    load(selected_stimuli)
    load(CONFIG_FILE)
    
    disp(['Usamos el texto ' filenames{idstimuli}])
    
    try       
%         answer = inputdlg('Ingrese solo las iniciales del sujeto', 'Nombre', 1, {'test'});
%         [~, title, ~] = fileparts(filenames{idstimuli});
%     
%         if isempty(answer)
%             return
%         else
%             initials  = upper(answer{1});
%             SAVE_PATH = fullfile(SAVE_PATH, initials);
%             filename  = fullfile(SAVE_PATH, filenames{idstimuli});
%             if exist(SAVE_PATH, 'dir') ~= 7
%                 mkdir(SAVE_PATH)
%             end
%         end
    
        if USE_EYETRACKER
            eyetrackerptr = initeyetracker(filename, screens, config);
        end
    
        [screenWindow, config] = initialize_screen(config, USE_EYETRACKER);
    
        showinitscreen(screenWindow, title, config)
        waitforkeypress
    
        % if USE_EYETRACKER
            validate_calibration(screenWindow, config)
        % end
    
        resetscreen(screenWindow, config.backgroundcolor)
        
        textures = nan(size(screens));
        for screenid = 1:length(screens)
            textures(screenid) = Screen('MakeTexture', screenWindow, screens(screenid).image);
        end
        
        t0 = GetSecs;
        trial = struct();
        trial.sujname  = initials;
        trial.file     = filename;
        trial.sequence = struct();
        sequenceid = 0;
        currentscreenid = 1;
        while 1
            sequenceid = sequenceid + 1;
            trial.sequence(sequenceid).currentscreenid = currentscreenid;        
            trial.sequence(sequenceid).timeini = GetSecs;
    
            if USE_EYETRACKER
                str = sprintf('ini %d %d', sequenceid, currentscreenid);
                eyetracker_message(str);
            end
    
            Screen('DrawTexture', screenWindow, textures(currentscreenid), []);
            Screen('Flip', screenWindow);       
    
            % Wait for a keypress
            while KbCheck;WaitSecs(0.001);end
            keypressed = get_keypress;
            
            resetscreen(screenWindow, config.backgroundcolor)        
            
            trial.sequence(sequenceid).timeend = GetSecs;        
            if USE_EYETRACKER
                str = sprintf('fin %d %d', sequenceid, currentscreenid);
                eyetracker_message(str);
            end    
    
            [currentscreenid, finish] = handlekeypress(keypressed, currentscreenid, length(screens), USE_EYETRACKER);
    
            if finish
                break
            end
        end
    
        fprintf('Tiempo: %2.2f\n', GetSecs - t0);    
        for screenid = 1:length(screens)
            Screen('close', textures(screenid));    
        end
        
        % if USE_EYETRACKER
            validate_calibration(screenWindow, config);   
        %    Eyelink('Command', 'clear_screen 0');
        % end
    
        returncontrol()
        Screen('CloseAll')
    
        if finish == 2
            trial.answers = show_questions(title);
        end
        
        save(filename, 'trial')
        
        
        if USE_EYETRACKER
            disp('Getting the file from the eyetracker')    
            if Eyelink('isconnected')
                eyelink_receive_file(filename)
            end
        end
        
    catch ME
        sca
        disp(ME) 
        returncontrol()
        disp('Hubo un error en run_experiment')
    
        if USE_EYETRACKER    
            Eyelink_end
        end
        keyboard
    end
    
    disp('Listo!')
end

function [currentscreenid, exit] = handlekeypress(keypressed, currentscreenid, maxscreens, USE_EYETRACKER)
    % exit = 2 -> story finished
    exit = 0;
    switch keypressed
        case 10
            disp('Pulsada tecla ESC, salimos.')
            exit = 1;
        case 115
            fprintf('Presionada flecha adelante, pantalla %d\n', currentscreenid);
            if currentscreenid == maxscreens
                if USE_EYETRACKER
                    str = sprintf('termina experimento');
                    eyetracker_message(str);
                end
                disp('Fin del experimento, salimos.')
                exit = 2;                    
            else
                currentscreenid = currentscreenid + 1;
            end
        case 114
            fprintf('Presionada flecha atras, pantalla %d\n', currentscreenid);
            currentscreenid = max(currentscreenid - 1, 1);                
        case 55 % C
            if USE_EYETRACKER
                calibrate_eyetracker(eyetrackerptr, screens, config)                 
            end                   
    end 
end

function waitforkeypress()
    while ~KbCheck;end
    while KbCheck;end
end

function returncontrol()
    ShowCursor;
    ListenChar(0);
    Priority(0);
end

function showinitscreen(screenptr, title, config)
    Screen('fillrect', screenptr, config.backgroundcolor);
    Screen('TextSize', screenptr, config.fontsize + 2);
    DrawFormattedText(screenptr, title, 100,  config.height * .3, config.textcolor); 
    Screen('TextSize', screenptr, config.fontsize / 2 + 3);
    DrawFormattedText(screenptr, 'Presione una tecla para seguir', 100,  config.height * .7, config.textcolor);
    Screen('Flip', screenptr);    
end

function resetscreen(screenptr, color)
    Screen('fillrect', screenptr, color);
    Screen('Flip', screenptr); 
end

function eyetrackerptr = initeyetracker(filename, screens, config)
    PARAMS.calBACKGROUND = config.backgroundcolor;
    PARAMS.calFOREGROUND = config.textcolor;
    [~, eyetrackerptr] = Eyelink_ini(filename, PARAMS);
    meanimage_transfer(screens, config);        
    sca
    WaitSecs(1);
end

function eyetracker_message(msg)
    if Eyelink('isconnected')
        str = sprintf('%s %d', msg, GetSecs);        
        Eyelink('Message', str);
    end
end
