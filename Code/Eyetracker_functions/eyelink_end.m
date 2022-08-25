function eyelink_end(edfFile)
% este programa hay que ponerlo antes de que cierre nuestro programa de
% matlab, es  para cerrar la comunicacion con el eyelink.

% finish up: stop recording eye-movements,
    % close graphics window, close data file and shut down tracker
    Eyelink('StopRecording');
    Eyelink('CloseFile');
    % Cierra  la comunicacion conel eyelink, hay que ponerlo solo si no
    % queremos recibir el archivo en esta compu, si no cometarlo y despues
    % de este correr eyelink_receive_file.m
    Eyelink('ShutDown');


    %Screen('CloseAll');   Ejecutar solo si despues nuestro  programa de
    %matlab no cierra el Screen del ptoolbox.
