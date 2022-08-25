%% ejemplo del uso del eyetracker
% bruno y diego 30/6/08

filename='mifile';
eyelink_ini(filename)%inicia la comuniucacion y calibra

  
disp('mi experimento')
for trial=1:3    
    str=['trial(' num2str(trial) ')'];
    Eyelink('Message', str); %mensaje de sincronizacion de cada trial
    disp(str)
    WaitSecs(0.500)
end
Screen('closeall')



%% parar y arrancar el guardado de datos, sirve para experimentos largos
%Eyelink('StopRecording');
%Eyelink('StartRecording');



%% miniexperimento con datos recolectados on line
tic
str=['Comienzo experimento con datos online'];
Eyelink('Message', str); %mensaje de sincronizacion de cada trial
while toc<20
    if Eyelink( 'NewFloatSampleAvailable') > 0 %se fija si hay un nuevo dato
        evt = Eyelink( 'NewestFloatSample'); % pide el dato actual
        
        %evt.time es eltiempo
        %evt.gx es un vector con [posxleft posxright] 
        %evt.gy es un vector con [posyleft posyright] 
        %evt.pa es un vector con [tampupilaleft tampupilaright] 

        %dibujo los datos colectados en la figura
        figure(1);cla;hold on
        set(gcf,'name','Ejemplito eyetracker')
        plot(evt.gx(1),evt.gy(1),'ob')
        plot(evt.gx(2),evt.gy(2),'or')        
        legend({'ojo izquierdo' 'ojo derecho'})
        xlim([0 1024])
        ylim([0 768])
        axis ij
        text(200,300,sprintf('tiempo: %d',evt.time))
        text(200,400,sprintf('Gx1: %8.2f   Gy1: %8.2f   Pa1 %8.2f',evt.gx(1),evt.gy(1),evt.pa(1)))
        text(200,500,sprintf('Gx2: %8.2f   Gy2: %8.2f   Pa2 %8.2f',evt.gx(2),evt.gy(2),evt.pa(2)))        
        setmouse(round(evt.gx(1)),round(evt.gy(1)))        
        drawnow
    
    end
end




Screen('closeall')
eyelink_end %finaliza comunicacion
eyelink_receive_file(filename) %recibe file de datos *.edf

disp(' ')
disp('hacer doble click sobre el file.edf para generar el file.asc')
disp('  y luego ejecutar todo=analiza_datos(''file.asc'') para los datos preprocesados')