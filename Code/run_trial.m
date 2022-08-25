function exit_status = run_trial(subjname, stimuli_index, stimuli_order, stimuli_questions, stimuli_config, save_path, use_eyetracker)
    % Constants
    STIMULI_PATH = 'Stimuli';
    keys.ESC = 10; % Windows: 27
    keys.NEXT = 115; % Windows: 39
    keys.BACK = 114; % Windows: 37
    keys.Ckey = 55; % Windows: 67
    
    Screen('Preference', 'SkipSyncTests', 1);
    Screen('Preference', 'VisualDebuglevel', 3); % remove presentation screen
    Screen('Preference', 'Verbosity', 1); % remove warnings

    title = stimuli_order{stimuli_index};

    selected_stimuli = fullfile(STIMULI_PATH, strcat(title, '.mat'));            
    load(selected_stimuli)

    disp(['Usamos el texto ' title])
    try
        eyelink_filename = strcat(subjname, '_', num2str(stimuli_index));
    
        eyetrackerptr = 0;
        if use_eyetracker
            eyetrackerptr = initeyetracker(eyelink_filename, screens, stimuli_config);
        end
    
        [screenWindow, stimuli_config] = initialize_screen(stimuli_config, use_eyetracker);

        keypressed = showcentertext(screenWindow, title, stimuli_config);
        if keypressed == keys.ESC
            finish_eyetracking(use_eyetracker)
            returncontrol()
            Screen('CloseAll')
            exit_status = 1;
            return
        end
    
        validate_calibration(screenWindow, stimuli_config, use_eyetracker)
        showcentertext(screenWindow, 'Ahora se presentara el texto. Lee con atencion.', stimuli_config)

        resetscreen(screenWindow, stimuli_config.backgroundcolor)
        
        textures = nan(size(screens));
        for screenid = 1:length(screens)
            textures(screenid) = Screen('MakeTexture', screenWindow, screens(screenid).image);
        end
        
        t0 = GetSecs;
        trial = struct();
        trial.subjname      = subjname;
        trial.stimuli_index = stimuli_index;
        trial.file          = selected_stimuli;
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

            keypressed = waitforkeypress();
            
            resetscreen(screenWindow, stimuli_config.backgroundcolor)        
            
            trial.sequence(sequenceid).timeend = GetSecs;        
            if use_eyetracker
                str = sprintf('fin %d %d', sequenceid, currentscreenid);
                eyetracker_message(str);
            end    
    
            [currentscreenid, exit_status] = handlekeypress(keypressed, keys, currentscreenid, ...
                length(screens), eyetrackerptr, stimuli_config, use_eyetracker);
    
            if exit_status > 0
                break
            end
        end
    
        fprintf('Tiempo: %2.2f\n', GetSecs - t0);    
        for screenid = 1:length(screens)
            Screen('close', textures(screenid));    
        end
        
        if exit_status ~= 1
            validate_calibration(screenWindow, stimuli_config, use_eyetracker);
        end
        
        finish_eyetracking(use_eyetracker)
    
        if exit_status == 2
            % Successful trial
            showcentertext(screenWindow, 'Termino el cuento! Ahora deberas responder unas preguntas y luego avisar al investigador', stimuli_config)
            trial.questions_answers = show_questions(screenWindow, title, stimuli_questions, stimuli_config, 'questions');
            showcentertext(screenWindow, 'Se presentaran palabras. Escribi la primera palabra que se te venga a la mente.', stimuli_config)
            trial.synonyms_answers  = show_questions(screenWindow, title, stimuli_questions, stimuli_config, 'synonyms');
        
            trial_filename = fullfile(save_path, title);
            save(trial_filename, 'trial')
        end

        returncontrol()
        Screen('CloseAll')
        
    catch ME
        sca
        disp(ME) 
        returncontrol()
        disp('Hubo un error en run_experiment')
    
        finish_eyetracking(use_eyetracker)
        keyboard
    end
    
    disp('Listo!')
end

function [currentscreenid, exit] = handlekeypress(keypressed, keys, currentscreenid, maxscreens, eyetrackerptr, stimuli_config, use_eyetracker)
    % exit = 2 -> story finished
    exit = 0;
    switch keypressed
        case keys.ESC
            disp('Pulsada tecla ESC, salimos.')
            exit = 1;
        case keys.NEXT
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
        case keys.BACK
            fprintf('Presionada flecha atras, pantalla %d\n', currentscreenid);
            currentscreenid = max(currentscreenid - 1, 1);                
        case keys.CKey
            if use_eyetracker
                calibrate_eyetracker(eyetrackerptr, screens, stimuli_config)                 
            end                   
    end 
end

function returncontrol()
    ShowCursor;
    ListenChar(0);
    Priority(0);
end

function resetscreen(screenptr, color)
    Screen('fillrect', screenptr, color);
    Screen('Flip', screenptr); 
end

function eyetrackerptr = initeyetracker(filename, screens, stimuli_config)
    PARAMS.calBACKGROUND = stimuli_config.backgroundcolor;
    PARAMS.calFOREGROUND = stimuli_config.textcolor;
    [~, eyetrackerptr] = eyelink_ini(filename, PARAMS);
    meanimage_transfer(screens, stimuli_config);        
    sca
    WaitSecs(1);
end

function finish_eyetracking(use_eyetracker)
    if use_eyetracker
       Eyelink('Command', 'clear_screen 0');
       eyelink_end
    end
end

function eyetracker_message(msg)
    if Eyelink('isconnected')
        str = sprintf('%s %d', msg, GetSecs);        
        Eyelink('Message', str);
    end
end
