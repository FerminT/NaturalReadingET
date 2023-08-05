function el=eyelink_set_default(el,PARAMS)
try

    % make sure we're still connected.
    if Eyelink('IsConnected')~=1
        return;
    end; 
    strings={}; %inicializo las celdas que van a contener las instrucciones

    
    
    
%% width y height son la resolucion actual de la pantalla en pixels (800,600; 1024,768; 640,480; etc)
    screens=Screen('Screens');
	whichScreen=max(screens);
    [width, height]=Screen('WindowSize', whichScreen);
    strings{end+1}=sprintf('screen_pixel_coords = %ld %ld %ld %ld', 0, 0, width-1, height-1);

%% CALIBRACION
    % set calibration type:
%     – H3: horizontal 3-point calibration
% – HV3: 3-point calibration, poor linearization
% – HV5: 5-point calibration, poor at corners
% – HV9: 9-point grid calibration, best overall
% – HV13: 13-point calibration for large calibration region (EyeLink II version 2.0 or later; Eye-
% Link 1000)
    strings{end+1}='calibration_type = HV9';
    strings{end+1}='calibration_area_proportion 0.88 0.83';
    strings{end+1}='validation_area_proportion 0.88 0.83';
    
    %Force manual accept
    strings{end+1}='enable_automatic_calibration = NO';
    
    %Pacing interval (solo en automatic)
    strings{end+1}='automatic_calibration_pacing = 1000';
        
    % (en binocular) if YES pregunta si queres usar solo el mejor ojo o los dos.
    strings{end+1}='select_eye_after_validation = NO';
    
    % eso
    strings{end+1}='cal_repeat_first_target = YES';
    strings{end+1}='val_repeat_first_target = YES';    

    % colors
    el.backgroundcolour = PARAMS.calBACKGROUND;
    el.foregroundcolour = PARAMS.calFOREGROUND;   

    
%%  File sample filter y link/analog filter y deteccion de eventos
    % 'heuristic_filter = <linkfilter> <filefilter>'
    % 0 or OFF disables link filter (OFF)
    % 1 or ON sets filter to 1 (moderate filtering, 1 sample delay) (STD)
    % 2 applies an extra level of filtering (2 sample delay). (EXTRA)
    strings{end+1}='heuristic_filter = 1 2';
    
    % sensitivity of saccade detector:
    % 0=standard
    % 1=high sensitivity saccade detector
    strings{end+1}='select_parser_configuration 0';
    
    % nada, dejar en GAZE
    strings{end+1}='recording_parse_type = GAZE';    
    
%     % set parser (conservative saccade thresholds)
%     Eyelink('command', 'saccade_velocity_threshold = 35');
%     % recheck this value!!! 30 for cognitive research, 22 for pursuit and
%     % neurological work
%     Eyelink('command', 'saccade_acceleration_threshold = 9500');
%     % recheck this value!!! 9500 for cognitive research, 5000 for pursuit
%     % and neurological work   
%% pupil_size_diameter = <YES or NO>
    % YES  diameter
    % NO  area 
    strings{end+1}='pupil_size_diameter = AREA';
    
%% DATA CONTENTS
    % set file and link event contents
    strings{end+1}='file_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON';
    strings{end+1}='link_event_filter = LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON';
    %strings{end+1}='file_event_data = GAZE,GAZERES,HREF,AREA,VELOCITY';%    %NO LO SETEAMOS
    %strings{end+1}='link_event_data = GAZE,GAZERES,HREF,FIXAVG,NOSTART';%    %NO LO SETEAMOS
    % el dafault: LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON    

    
    % set file and link sample contents    
    strings{end+1}='file_sample_data  = LEFT,RIGHT,GAZE,AREA';
    strings{end+1}='link_sample_data  = LEFT,RIGHT,GAZE,AREA';    
    % default para remoto       LEFT,RIGHT,GAZE,GAZERES,HTARGET,AREA,STATUS
    % default para no remoto    LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS
    % el que usamos nosotros para analiza_datos   LEFT,RIGHT,GAZE,AREA
    
    
    
     
    

    

    
    
%%    escribo las instrucciones en el eyetracker, y las muestro
    disp('Escribiendo configuración en el EYETRACKER:')
    for i=1:length(strings)
        disp(['   ' strings{1,i}])
        Eyelink('command',strings{1,i});
        Eyelink('message',strings{1,i});
    end
    disp('Configuración escrita.')   
  

        % make sure we're still connected.
    if Eyelink('IsConnected')~=1
        return;
    end; 
catch 
    sca
    keyboard
end
end