function exit_status = run_trial(subjname, stimuli_index, stimuli_order, stimuli_config, save_path, use_eyetracker)
    % addpath('C:\Documents and Settings\Diego\Mis documentos\Dropbox\_LABO\eyetracker_Funciones')
    
    Screen('Preference', 'SkipSyncTests', 1);
    Screen('Preference', 'VisualDebuglevel', 3); % remove presentation screen
    Screen('Preference', 'Verbosity', 1); % remove warnings

    title = stimuli_order{stimuli_index};

    STIMULI_PATH     = 'Stimuli';
    selected_stimuli = fullfile(STIMULI_PATH, strcat(title, '.mat'));            
    load(selected_stimuli)

    disp(['Usamos el texto ' title])
    try
        eyelink_filename = strcat(subjname, '_', num2str(stimuli_index));
    
        if use_eyetracker
            eyetrackerptr = initeyetracker(eyelink_filename, screens, stimuli_config);
        end
    
        [screenWindow, stimuli_config] = initialize_screen(stimuli_config, use_eyetracker);
    
        showinitscreen(screenWindow, title, stimuli_config)
        waitforkeypress
    
        validate_calibration(screenWindow, stimuli_config)
    
        resetscreen(screenWindow, stimuli_config.backgroundcolor)
        
        textures = nan(size(screens));
        for screenid = 1:length(screens)
            textures(screenid) = Screen('MakeTexture', screenWindow, screens(screenid).image);
        end
        
        t0 = GetSecs;
        trial = struct();
        trial.subjname = subjname;
        trial.file     = selected_stimuli;
        trial.sequence = struct();
        sequenceid = 0;
        currentscreenid = 1;
        while 1
            sequenceid = sequenceid + 1;
            trial.sequence(sequenceid).currentscreenid = currentscreenid;        
            trial.sequence(sequenceid).timeini = GetSecs;
    
            if use_eyetracker
                str = sprintf('ini %d %d', sequenceid, currentscreenid);
                eyetracker_message(str);
            end
    
            Screen('DrawTexture', screenWindow, textures(currentscreenid), []);
            Screen('Flip', screenWindow);       
    
            % Wait for a keypress
            while KbCheck;WaitSecs(0.001);end
            keypressed = get_keypress;
            
            resetscreen(screenWindow, stimuli_config.backgroundcolor)        
            
            trial.sequence(sequenceid).timeend = GetSecs;        
            if use_eyetracker
                str = sprintf('fin %d %d', sequenceid, currentscreenid);
                eyetracker_message(str);
            end    
    
            [currentscreenid, exit_status] = handlekeypress(keypressed, currentscreenid, length(screens), use_eyetracker);
    
            if exit_status > 0
                break
            end
        end
    
        fprintf('Tiempo: %2.2f\n', GetSecs - t0);    
        for screenid = 1:length(screens)
            Screen('close', textures(screenid));    
        end
        
        validate_calibration(screenWindow, stimuli_config);   
        if use_eyetracker
           Eyelink('Command', 'clear_screen 0');
        end
    
        returncontrol()
        Screen('CloseAll')
    
        if exit_status == 2
            trial.answers = show_questions(title);
        end
        
        trial_filename = fullfile(save_path, title);
        save(trial_filename, 'trial')

        if use_eyetracker
            disp('Getting the file from the eyetracker')    
            if Eyelink('isconnected')
                eyelink_receive_file(eyelink_filename)
            end
        end
        
    catch ME
        sca
        disp(ME) 
        returncontrol()
        disp('Hubo un error en run_experiment')
    
        if use_eyetracker    
            Eyelink_end
        end
        keyboard
    end
    
    disp('Listo!')
end

function [currentscreenid, exit] = handlekeypress(keypressed, currentscreenid, maxscreens, use_eyetracker)
    % exit = 2 -> story finished
    exit = 0;
    switch keypressed
        case 10
            disp('Pulsada tecla ESC, salimos.')
            exit = 1;
        case 115
            fprintf('Presionada flecha adelante, pantalla %d\n', currentscreenid);
            if currentscreenid == maxscreens
                if use_eyetracker
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
            if use_eyetracker
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
