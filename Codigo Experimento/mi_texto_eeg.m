function mi_texto(numtexto)
fprintf('JK (08/06/2013): Sólo incluí las marcas del EEG, después de cada mensaje al Eye Tracker, igual que en la última versión del mi_precalibracion_v2.m (según JK (08/11/2012)). \n')
addpath('J:\eyetracker\funciones')
if ~exist('numtexto','var')
    disp('Tenés que definir el texto (1:10)')
    return
end
Screen('Preference', 'SkipSyncTests', 1);
Screen('Preference', 'VisualDebuglevel', 3);% para que no aparezca la pantalla de presentacion
Screen('Preference', 'Verbosity', 1);% para que no muestre los warnings

textos={'1 Carta abierta' '2 Bienvenido Bob' '3 axolotl' '4 SOMBRAS SOBRE VIDRIO ESMERILADO 1' '4 SOMBRAS SOBRE VIDRIO ESMERILADO 2' '5 El origen de las especies' '6 sacks - rebeca' '7 El loco Cansino' '8 El Negro de Paris' '9 Carta a una senorita en Paris'};
TITULOS={'CARTA ABIERTA A LA JUNTA MILITAR- Rodolfo Walsh' ...
'BIENVENIDO BOB - Juan Carlos Onetti' ...
'AXOLOTL - Julio Cortazar' ...
'SOMBRAS SOBRE VIDRIO ESMERILADO - Juan José Saer (parte 1)' ...
'SOMBRAS SOBRE VIDRIO ESMERILADO - Juan José Saer (parte 2)' ...
'Introducción de EL ORIGEN DE LAS ESPECIES - Charles Darwin' ...
'REBECA - Oliver Sacks' ...
'El loco Cansino - Roberto Fontanarrosa' ...
'El Negro de París - Osvaldo Soriano' ...
'Carta a una señorita en París - Julio Cortázar'};

load(textos{numtexto})%cargo las variables necesarias, texto y pantallas.
disp(['Usamos el texto ' textos{numtexto} ': ' TITULOS{numtexto}])

USOEYETRACKER 	= 1;%0=No, 1=Si
USOEEG          = 1;%0=No, 1=Si

try       
    %pregunta el nombre del sujeto
    answer = inputdlg('Ingrese su nombre','Nombre',1,{'test'});
    %answer={'test'};
    if isempty(answer)
        return %si aprietan cancel, sale
    else
        filename=[answer{1} '_' num2str(numtexto)];
    end
    if USOEYETRACKER
        PARAMS.calBACKGROUND = init.colorfondo;
        PARAMS.calFOREGROUND = init.colortexto;
        eyelink_ini(filename,PARAMS)
        sca
    end
    % Empieza
    if USOEEG
        dio= digitalio('parallel','LPT1');
        out_lines=addline(dio,0:7,0,'out'); % primero es el objeto creado para mandar info, 0:7 las lineas del objeto a usar, 0 la linea del digital port creado, y 'out' si es entrada o salida (en este caso salida)
        putvalue(dio.line(1:8),dec2binvec(0,8));
    end

    [w init]=inicializa_pantalla(init);
    
    %Priority(1);
    
    if USOEYETRACKER
        pseudo_calibracion(w,init);
    end
            
    Screen('fillrect',w,init.colorfondo)%borra la pantalla
    Screen('TextSize',w, init.fontsize);
    DrawFormattedText(w, TITULOS{numtexto}, 100,  init.height*.3, init.colortexto); 
    Screen('TextSize',w, init.fontsize/2);
    DrawFormattedText(w, 'Pulse una tecla para seguir', 100,  init.height*.7, init.colortexto);
    Screen('Flip',w);               
    while ~KbCheck;WaitSecs(0.001);end%espero a que toque una tecla
    while KbCheck;WaitSecs(0.001);end%espero a que la suelte
    Screen('fillrect',w,init.colorfondo)%borra la pantalla
    Screen('Flip',w);               
    
    trial=struct();
    trialnum=0;
    init.currentscreen=1;   
    
    texturas=nan(size(pantallas));
    for indpant=1:length(pantallas)
        texturas(indpant)=Screen('maketexture',w,pantallas(indpant).imagen);
    end
    
    tinicial=GetSecs;
    while 1
        trialnum=trialnum+1;
        trial(trialnum).sujname=filename;
        trial(trialnum).currentscreen=init.currentscreen;        
        trial(trialnum).timeini=GetSecs;        
        if USOEYETRACKER
            str=sprintf('ini %d %d',trialnum,init.currentscreen);
            mensaje_eyetracker(str);
        end
	if USOEEG
	    putvalue(dio.line(1:8),dec2binvec(init.currentscreen,8)); 
	    WaitSecs(0.01);
	    putvalue(dio.line(1:8),dec2binvec(0,8));
	end
        Screen('drawtexture',w,texturas(init.currentscreen),[]);
        %DrawFormattedText(w, num2str(init.currentscreen), 50,  50, init.colortexto); 
        Screen('Flip',w);       
        while KbCheck;WaitSecs(0.001);end        
        resp_button=get_resp;   %espera a que toques una tecla
        
        Screen('fillrect',w,init.colorfondo)%borra la pantalla
        Screen('Flip',w);               
        
        trial(trialnum).timeend=GetSecs;        
        if USOEYETRACKER
            str=sprintf('fin %d %d',trialnum,init.currentscreen);
            mensaje_eyetracker(str);
        end
	if USOEEG
	    putvalue(dio.line(1:8),dec2binvec(100+init.currentscreen,8)); 
	    WaitSecs(0.01);
	    putvalue(dio.line(1:8),dec2binvec(0,8));
	end

        switch resp_button
            case 27%salimos
                disp('Pulsada tecla ESC, salimos.')
                break
            case 39%pagina siguiente
                fprintf('Pulsada flecha adelante, pantalla %d\n',init.currentscreen);
                if init.currentscreen==length(pantallas)
                    if USOEYETRACKER
                        str=sprintf('termina experimento');
                        mensaje_eyetracker(str);
                    end
		    if USOEEG
	    		putvalue(dio.line(1:8),dec2binvec(200,8)); 
	    		WaitSecs(0.01);
	    		putvalue(dio.line(1:8),dec2binvec(0,8));
		    end
                    disp('Fin del experimento, salimos.')
                    break                    
                else
                    init.currentscreen=init.currentscreen+1;
                end
                
                %ya avancé
            case 37%pagina anterior
                fprintf('Pulsada flecha atras, pantalla %d\n',init.currentscreen);
                init.currentscreen=max(init.currentscreen-1,1);                
%             case 40%pausa
%                 while KbCheck;WaitSecs(0.001);end  
%                 if USOEYETRACKER
%                     str=sprintf('Inicio_pausa');
%                     mensaje_eyetracker(str);
%                 end
%                 fprintf('Pulsada pausa, pantalla %d\n',init.currentscreen);
%                 Screen('FillRect', w, init.colorfondo);%fondo blanco
%                 Screen('TextSize',w, init.fontsize*2);
%                 DrawFormattedText(w, 'Pulse una tecla para seguir', 100,  init.height*.7, init.colortexto); 
%                 Screen('Flip',w);
%                 get_resp;                                
%                 while KbCheck;WaitSecs(0.001);end                       
%                 if USOEYETRACKER
%                     str=sprintf('Fin_pausa');
%                     mensaje_eyetracker(str);
%                 end                
        end        
    end
    fprintf('Tiempo: %2.2f\n',GetSecs-tinicial);    
    for indpant=1:length(pantallas)
        Screen('close',texturas(indpant));    
    end
    
    if USOEYETRACKER
        pseudo_calibracion(w,init);    
    end
    
    if exist('data','dir')~=7;mkdir('data');end
    save(['./data/' filename],'trial','texto','init','pantallas')
    
    ShowCursor;%muestra el cursor
    ListenChar(0)%vuelve a la normalidad. si no pude ejecutarlo, ctrl+c hace lo mismo        
    Screen('CloseAll')%cierra todo
    Priority(0);
    
    if USOEYETRACKER
        disp('Pido el archivo de eyetracker')    
        if eyelink('isconnected')
            eyelink_receive_file(filename)
        end
    end
    
catch ME %% cierro todo si algo falla
    sca
    disp(ME) 
    ShowCursor;%muestra el cursor
    disp('Hubo un error en mi_experimento!!!')
    ListenChar(0)%vuelve a la normalidad. si no pude ejecutarlo, ctrl+c hace lo mismo        
    Priority(0);
    if USOEYETRACKER    
        eyelink_end
    end
    keyboard
end
disp('listo!')        

end

function [w init]=inicializa_pantalla(init)
% inicializa pantalla
try
    screenNumber=max(Screen('Screens'));
    w = Screen('OpenWindow', screenNumber, 0,init.windowrect, 32, 2);
    Screen(w,'BlendFunction',GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    %Screen('TextFont', w, 'Courier New');
    %Screen('TextSize', w, 20);%ver tamaï¿½o
    if isempty(init.windowrect)
        HideCursor; %oculta el cursos
    end
    ListenChar(2)%hace que los keypresses no se vean en matlab editor (ojo hay que habilitarlo al final del programa!)
    disp('Pantalla inicializada')
    
    init.fps=Screen('FrameRate',w);      % frames per second
    init.ifi=1/init.fps;%inter-frame interval (no lo hago con getflipinterval porque ese mide, y este redondea.
    [init.width, init.height]=Screen('WindowSize', w);
    init.CX=round(init.width/2);
    init.CY=round(init.height/2);
catch ME
    Screen('CloseAll')
    ShowCursor;%muestra el cursor
    ListenChar(0)%vuelve a la normalidad. si no pude ejecutarlo, ctrl+c hace lo mismo
    disp('Hubo un error en inicializa_pantalla()!!!')
    disp(ME)
    if USOEYETRACKER    
        eyelink_end
    end    
    
end
end

function mensaje_eyetracker(msg)
    if Eyelink('isconnected')
        str=sprintf('%s %d',msg,GetSecs);        
        Eyelink('Message', str);
    end
end

function pseudo_calibracion(window,init)   
    xx=[.2 .5 .8 .2 .5 .8 .2 .5 .8]*init.width;
    yy=[.2 .2 .2 .5 .5 .5 .8 .8 .8]*init.height;
    
    Screen('FillRect', window,init.colorfondo);
    Screen('TextSize', window, 20);%ver tamaï¿½o    
    Screen('DrawText', window, 'Mire los puntitos que aparecen',init.CX-200,init.CY-100,init.colortexto);
    Screen('DrawText', window, 'Pulse una tecla para comenzar ',init.CX-200,init.CY,init.colortexto);
    t=GetSecs;Screen('Flip', window,t+init.ifi); 
    while ~KbCheck;end %espero a que toque una tecla
    while KbCheck;end %espero a que la suelte
    waitsecs(.5);  
    
    for i=1:length(xx)             
        Screen('FillRect', window,init.colorfondo);
        ssize=10;
        poscirculo=[xx(i)-ssize yy(i)-ssize xx(i)+ssize yy(i)+ssize];       
        Screen('FillOval', window,init.colortexto, poscirculo);
        ssize=2;
        poscirculo=[xx(i)-ssize yy(i)-ssize xx(i)+ssize yy(i)+ssize];       
        Screen('FillOval', window,init.colorfondo, poscirculo);
        t=GetSecs;Screen('Flip', window,t+init.ifi); 
        str=['pseudocalib ' num2str(xx(i)) ',' num2str(yy(i)) ];
        if eyelink('isconnected');Eyelink('Message', str);end  
        [tresp condicion]=espera_posicion_ojo([xx(i) yy(i)],30,0);%espero a que el ojo este en donde la primera letra
        Screen('FillRect', window,init.colorfondo);
        ssize=10;
        poscirculo=[xx(i)-ssize yy(i)-ssize xx(i)+ssize yy(i)+ssize];       
        Screen('FillOval', window,init.colortexto, poscirculo);        
        ssize=2;
        poscirculo=[xx(i)-ssize yy(i)-ssize xx(i)+ssize yy(i)+ssize];       
        Screen('FillOval', window,[255 0 0], poscirculo);
        
        t=GetSecs;Screen('Flip', window,t+init.ifi); 
        if condicion==2%si toca una tecla, salgo
            break
        end
        waitsecs(0.5);        
    end
    Screen('FillRect', window,init.colorfondo);
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
