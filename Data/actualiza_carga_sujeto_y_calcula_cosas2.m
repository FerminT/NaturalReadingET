%%
crudopath = 'C:\Documents and Settings\LNI\Mis documentos\Dropbox\crudosExp2\';

% En la compu de Julia:
expepath='C:\Documents and Settings\LNI\Mis documentos\Dropbox\reading\data_expe2\';
addpath('C:\Documents and Settings\LNI\Mis documentos\Dropbox\reading\analisis2\my_functions')
cd('C:\Documents and Settings\LNI\Mis documentos\Dropbox\reading\analisis2')

% %En la compu de Diego:
% expepath='E:\Dropbox\_LABO\reading\data_expe2\';
% addpath('E:\Dropbox\_LABO\reading\analisis2\my_functions')
% cd('E:\Dropbox\_LABO\reading\analisis2')

[suj gruponames]=cargo_lista_sujetos2(crudopath,expepath);


for su=25

    disp(['%%%%%%%%%% ' suj(su).filename ' %%%%%%%%%%%%%%%%%%%'])    
    RECALCULA.todo=1;          %1= usa solo los datos salidos del experimento, y recalcula todo de nuevo
    RECALCULA.renglones=0;     %1= GUI para redefinir la asignacion de fijaciones a cada renglon. RECALCULA TODO lo que sigue
    RECALCULA.FIX=0;           %1= recalcula la estructura de fijaciones a partir de lo que viene del eyetracker. agrega frec, catgram, asignacion a palabras. y recalcula palabras
    RECALCULA.FIXborradas=0;   %1= permite modificar las FIX descartadas, removidas, las primeras y ultimas de cada trial. y recalcula palabras
    RECALCULA.palabras=1;      %1= recalcula la estructura de palabras, a partir de las fijaciones y el texto.


    [init pantallas todo trial texto expe FIX palabras]=carga_sujeto_y_calcula_cosas2(suj(su), RECALCULA);
end

