function openejecutable(ejecutable, T);

% Inicializa el eyelink, abra un ejecutable enviando un mensaje cuando esto sucede y queda grabando por un tiempo
% T. Luego cierra termina e grabar y cierra el archivo pero no lo pide.

[edfFile]=eyelink_ini();

Waitsecs(1);              
Screen('CloseAll');

open(ejecutable);
Eyelink('Message', 'Empieza programa');
Waitsecs(T);
Eyelink('StopRecording');
Eyelink('CloseFile');
