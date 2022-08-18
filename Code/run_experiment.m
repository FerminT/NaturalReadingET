% addpath('C:\Documents and Settings\Diego\Mis documentos\Dropbox\_LABO\eyetracker_Funciones')

Screen('Preference', 'SkipSyncTests', 1);
Screen('Preference', 'VisualDebuglevel', 3); % remove presentation screen
Screen('Preference', 'Verbosity', 1); % remove warnings

config_file  = fullfile('..', 'stimuli_config.mat');
stimuli_path = fullfile('..', 'Stimuli');
save_path    = fullfile('..', 'Data');

files      = dir(stimuli_path);
filenames  = string({files([files.isdir] == 0).name});

% Si vamos a seguir un orden, cargar stimuli_order.mat y usar eso como
% filenames. Si no, hacer random sobre filenames.

[idstimuli, ok] = listdlg('PromptString','Elija un texto a presentar:', ...
                'SelectionMode','single', ...
                'ListSize', [400 300], ...
                'ListString', filenames);
if ok == 0
    return
end

selected_stimuli = fullfile(stimuli_path, filenames{idstimuli});            
load(selected_stimuli)
load(config_file)

disp(['Usamos el texto ' filenames{idstimuli}])

use_eyetracker = 0;

try       
    answer = inputdlg('Ingrese solo las iniciales del sujeto', 'Nombre', 1, {'test'});
    [path, filename, extension] = fileparts(filenames{idstimuli});

    if isempty(answer)
        return
    else
        initials  = upper(answer{1});
        save_path = fullfile(save_path, initials);
        if exist(save_path, 'dir') ~= 7
            mkdir(save_path)
        end
    end

    if use_eyetracker
        PARAMS.calBACKGROUND = config.backgroundcolor;
        PARAMS.calFOREGROUND = config.textcolor;
        [edfFile el] = eyelink_ini(filename, PARAMS);
        transfiere_imagen_promedio(config, screens);        
        sca
        WaitSecs(1);
    end

    [screenWindow config] = initialize_screen(config, use_eyetracker);
    
    if use_eyetracker
        pseudo_calibracion(screenWindow, config);
    end
            
    Screen('fillrect', screenWindow, config.backgroundcolor)
    Screen('TextSize', screenWindow, config.fontsize);
    DrawFormattedText(screenWindow, filename, 100,  config.height * .3, config.textcolor); 
    Screen('TextSize', screenWindow, config.fontsize / 2);
    DrawFormattedText(screenWindow, 'Pulse una tecla para seguir', 100,  config.height * .7, config.textcolor);
    Screen('Flip', screenWindow);     

    % Wait for a keypress
    while ~KbCheck;WaitSecs(0.001);end
    while KbCheck;WaitSecs(0.001);end

    Screen('fillrect', screenWindow, config.backgroundcolor)
    Screen('Flip', screenWindow);               
    
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

        if use_eyetracker
            str = sprintf('ini %d %d', sequenceid, currentscreenid);
            mensaje_eyetracker(str);
        end

        Screen('DrawTexture', screenWindow, textures(currentscreenid), []);
        Screen('Flip', screenWindow);       

        % Wait for a keypress
        while KbCheck;WaitSecs(0.001);end
        resp_key = get_resp;
        
        Screen('fillrect', screenWindow, config.backgroundcolor)
        Screen('Flip', screenWindow);               
        
        trial.sequence(sequenceid).timeend = GetSecs;        
        if use_eyetracker
            str = sprintf('fin %d %d', sequenceid, currentscreenid);
            mensaje_eyetracker(str);
        end    

        switch resp_key
            case 10
                disp('Pulsada tecla ESC, salimos.')
                break
            case 115
                fprintf('Presionada flecha adelante, pantalla %d\n', currentscreenid);
                if currentscreenid == length(screens)
                    if use_eyetracker
                        str = sprintf('termina experimento');
                        mensaje_eyetracker(str);
                    end
                    disp('Fin del experimento, salimos.')
                    break                    
                else
                    currentscreenid = currentscreenid + 1;
                end
            case 114
                fprintf('Presionada flecha atras, pantalla %d\n', currentscreenid);
                currentscreenid = max(currentscreenid - 1, 1);                
            case 55
                if use_eyetracker
                    Eyelink('StopRecording');    

                    % Calibrate the eye tracker
                    EyelinkDoTrackerSetup(el);
                    EyelinkDoDriftCorrection(el);
                    FlushEvents('keydown')

                    transfiere_imagen_promedio(config, screens);        
                    
                    Eyelink('StartRecording');                    
                end                   
        end        
    end
    fprintf('Tiempo: %2.2f\n', GetSecs - t0);    
    for screenid = 1:length(screens)
        Screen('close', textures(screenid));    
    end
    
    if use_eyetracker
        pseudo_calibracion(screenWindow, config);    
        Eyelink('Command', 'clear_screen 0');
    end
    
    save(fullfile(save_path, filename), 'trial')
    
    ShowCursor;
    ListenChar(0)
    Screen('CloseAll')
    Priority(0);
    
    if use_eyetracker
        disp('Getting the file from the eyetracker')    
        if eyelink('isconnected')
            eyelink_receive_file(fullfile(save_path, filename))
        end
    end
    
catch ME
    sca
    disp(ME) 
    ShowCursor;
    disp('Hubo un error en run_experiment')
    ListenChar(0)
    Priority(0);
    if use_eyetracker    
        eyelink_end
    end
    keyboard
end
disp('Listo!')

function mensaje_eyetracker(msg)
    if Eyelink('isconnected')
        str=sprintf('%s %d',msg,GetSecs);        
        Eyelink('Message', str);
    end
end

function pseudo_calibracion(window,config)   
    xx=[.2 .5 .8 .2 .5 .8 .2 .5 .8]*config.width;
    yy=[.2 .2 .2 .5 .5 .5 .8 .8 .8]*config.height;
    
    Screen('FillRect', window,config.colorfondo);
    Screen('TextSize', window, 20);%ver tama�o    
    Screen('DrawText', window, 'Mire los puntitos que aparecen',config.CX-200,config.CY-100,config.colortexto);
    Screen('DrawText', window, 'Pulse una tecla para comenzar ',config.CX-200,config.CY,config.colortexto);
    t=GetSecs;Screen('Flip', window,t+config.ifi); 
    while ~KbCheck;end %espero a que toque una tecla
    while KbCheck;end %espero a que la suelte
    waitsecs(.5);  
    
    for i=1:length(xx)             
        Screen('FillRect', window,config.colorfondo);
        ssize=10;
        poscirculo=[xx(i)-ssize yy(i)-ssize xx(i)+ssize yy(i)+ssize];       
        Screen('FillOval', window,config.colortexto, poscirculo);
        ssize=3;
        poscirculo=[xx(i)-ssize yy(i)-ssize xx(i)+ssize yy(i)+ssize];       
        Screen('FillOval', window,config.colorfondo, poscirculo);
        t=GetSecs;Screen('Flip', window,t+config.ifi); 
        str=['pseudocalib ' num2str(xx(i)) ',' num2str(yy(i)) ];
        if eyelink('isconnected');Eyelink('Message', str);end  
        [tresp condicion]=espera_posicion_ojo([xx(i) yy(i)],30,0);%espero a que el ojo este en donde la primera letra
        Screen('FillRect', window,config.colorfondo);
        ssize=10;
        poscirculo=[xx(i)-ssize yy(i)-ssize xx(i)+ssize yy(i)+ssize];       
        Screen('FillOval', window,config.colortexto, poscirculo);        
        ssize=3;
        poscirculo=[xx(i)-ssize yy(i)-ssize xx(i)+ssize yy(i)+ssize];       
        Screen('FillOval', window,[0 128 0], poscirculo);
        
        t=GetSecs;Screen('Flip', window,t+config.ifi); 
        if condicion==2%si toca una tecla, salgo
            break
        end
        waitsecs(0.5);        
    end
    Screen('FillRect', window,config.colorfondo);
    Screen('Flip', window); 
end

function [tresp condicion]=espera_posicion_ojo(posicion,tamanio,tiempomax)
%[tresp condicion]=espera_posicion_ojo([512 384],30,0);
%condicion: 0->ojo entro a la region 1->timeout 2->teclado 3->mouse
    tstart=GetSecs;
    while 1
        [x,y,buttons] = GetMouse;
        if max(buttons)>0 % si toca boton mouse sale con condicion 3
            while any(buttons)
                [x,y,buttons] = GetMouse;
            end
            condicion=3;
            break             
        end
        if KbCheck %si toca una tecla salgo con condicion 2
            condicion=2;
            while KbCheck;end % espera a que sueltes el teclado
            break 
        end
        if tiempomax>0 && GetSecs-tstart<tiempomax    %si pasa el tiempomax  salgo con condicion 1
           condicion=1;
           break
        end
        if eyelink('isconnected')
            if Eyelink( 'NewFloatSampleAvailable') > 0 %se fija si hay un nuevo dato
                evt = Eyelink( 'NewestFloatSample'); % pide el dato actual
                %evt.time es eltiempo
                %evt.gx es un vector con [posxleft posxright] 
                %evt.gy es un vector con [posyleft posyright] 
                %evt.pa es un vector con [tampupilaleft tampupilaright] 
                distleft =sqrt((evt.gx(1)-posicion(1))^2+(evt.gy(1)-posicion(2))^2);
                distright=sqrt((evt.gx(2)-posicion(1))^2+(evt.gy(2)-posicion(2))^2);            
                if distleft<tamanio || distright<tamanio %si ojo posicion salgo con condicion 0
                    condicion=0;
                    break
                end
            end
        end
    end
    tresp=GetSecs-tstart;    
end

function [resp_button,tresp]=get_resp()
% get_resp: espera una tecla y reporta la tecla y el tiempo

keyIsDown=0;
tstart=GetSecs;
while keyIsDown==0 %hasta que presione una tecla
    [ keyIsDown, seconds, keyCode ]=KbCheck;
    WaitSecs(0.001);%para que todo fluya bien
end
tresp=seconds-tstart;  %guarda info
resp_button=find(keyCode==1);
resp_button=resp_button(1);%(para que devuelva una sola tecla si tocas mas de una)

end

function transfiere_imagen_promedio(config,pantallas)
I=zeros(size(pantallas(1).imagen));
for i=1:length(pantallas)    
    I=or(I,pantallas(i).imagen==0);
end
I=config.colorfondo*(1-I);

imwrite(I,'imagen.bmp');
finfo = imfinfo('imagen.bmp');
finfo.Filename 
Eyelink('StopRecording');
transferStatus = Eyelink('ImageTransfer', finfo.Filename ,0,0,0,0,round(config.width/2 - finfo.Width/2) ,round(config.height/2 - finfo.Height/2),4);
if transferStatus ~= 0
    fprintf('Image to host transfer failed\n');
end
WaitSecs(0.1);
Eyelink('StartRecording');

end
