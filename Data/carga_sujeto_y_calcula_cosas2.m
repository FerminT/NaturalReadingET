function [init pantallas todo trial texto expe FIX palabras]=carga_sujeto_y_calcula_cosas2(suj, RECALCULA)
%     RECALCULA.todo=0;          %1= usa solo los datos salidos del experimento, y recalcula todo de nuevo
%     RECALCULA.renglones=0;     %1= GUI para redefinir la asignacion de fijaciones a cada renglon. RECALCULA TODO lo que sigue
%     RECALCULA.FIX=0;           %1= recalcula la estructura de fijaciones a partir de lo que viene del eyetracker. agrega frec, catgram, asignacion a palabras. y recalcula palabras
%     RECALCULA.FIXborradas=0;   %1= permite modificar las FIX descartadas, removidas, las primeras y ultimas de cada trial. y recalcula palabras
%     RECALCULA.palabras=0;      %1= recalcula la estructura de palabras, a partir de las fijaciones y el texto.


try
    tic   
    fprintf('Calculamos %s\n',suj.filename)

    if ~isfield(RECALCULA,'renglones'); RECALCULA.renglones = 0;    end
    if ~isfield(RECALCULA,'FIX');       RECALCULA.FIX   = 0;    end
    if ~isfield(RECALCULA,'palabras');  RECALCULA.palabras = 0; end
    if ~isfield(RECALCULA,'FIXborradas');RECALCULA.FIXborradas = 0; end
    
    
    %cargo (o calculo) todo
    if  ~exist([suj.crudopath,suj.filename '_todo.mat'],'file') % Si no existe lo calcula
        load([suj.crudopath,suj.filename]) %tiene init, pantallas, texto y trial
        todo=analiza_datos([suj.crudopath,suj.filename '.asc']);
        save([suj.crudopath,suj.filename '_todo'],'todo')
        fprintf('Creo y guardo %s_todo.mat, t=%gseg\n',suj.filename, toc )
    else
        load([suj.crudopath,suj.filename '_todo'])         
        fprintf('Cargo %s_todo.mat, t=%gseg\n',suj.filename, toc )
    end
        
    %cargo los datos iniciales del experimento
    load([suj.crudopath,suj.filename]) %tiene init, pantallas, texto y trial
    fprintf('Cargo %s.mat (tiene init, pantallas, texto y trial), t=%gseg\n',suj.filename, toc )

    %si no existe, creo la estructura de fijaciones
    if ~exist('FIX','var')
        FIX = struct();
    end    

    %cargo (o creo) expe
    if exist([suj.expepath,suj.filename '_expe.mat'],'file') && ~RECALCULA.todo
        load([suj.expepath,suj.filename '_expe']) 
        fprintf('Cargo %s_expe.mat (tiene FIX, expe, init, palabras, pantallas, texto, trial), t=%gseg\n',suj.filename, toc )
    else
        expe.filename   = suj.filename;
        expe.ojo        = suj.ojo;
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial')
        fprintf('Creo y guardo %s_expe.mat (vacio), t=%gseg\n',suj.filename, toc )        
    end
    
    %agrego el tiempo del eyetracker al trial
    if ~isfield(trial,'timeetini')  || RECALCULA.todo   %#ok<NODEF>
        trial=agrego_tiempo_ET_a_trial(todo,trial);
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial')
        fprintf('Agrego el tiempo del eyetracker al trial y guardo %s_expe.mat, t=%gseg\n',suj.filename, toc )        
    end

    %defino los renglones, esto queremos hacerlo una sola vez
    if ~isfield(trial,'renglones')  || RECALCULA.todo   || RECALCULA.renglones
        trial=defino_renglones(init, pantallas, todo, trial, texto, expe); %#ok<NODEF>
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial')
        fprintf('Defino los renglones y guardo %s_expe.mat, t=%gseg\n',suj.filename, toc )               
        fprintf('\tDebo recalcular todo lo que viene tambien: RECALCULA.todo=1 \n')               
        RECALCULA.todo=1;
    end

    %defino ancho de los caracteres
    if ~isfield(expe,'anchocaracter') || RECALCULA.todo 
        expe=defino_ancho_caracter(expe,texto);
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial')
        fprintf('Defino ancho de los caracteres y guardo %s_expe.mat, t=%gseg\n',suj.filename, toc )               
    end

    %defino espacios en el texto
    if ~isfield(texto,'espacios')   || RECALCULA.todo   
        texto=defino_espacios_en_texto(texto,expe,init);
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial')    
        fprintf('Defino espacios en el texto y guardo %s_expe.mat, t=%gseg\n',suj.filename, toc )               
    end

    %defino las fijaciones
    if ~isfield(FIX,'renglon')      || RECALCULA.todo   || RECALCULA.FIX
        FIX=defino_FIX(todo, trial, expe);
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial')    
        fprintf('Defino FIX y guardo %s_expe.mat, t=%gseg\n',suj.filename, toc )               
    end

    %asigno las fijaciones a las palabras
    if ~isfield(FIX,'longpalabra')  || RECALCULA.todo  || RECALCULA.FIX 
        FIX=asigno_fijaciones_a_palabras(FIX,texto,expe);
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial')    
        fprintf('Asigno fijaciones a palabras (en FIX) y guardo %s_expe.mat, t=%gseg\n',suj.filename, toc )               
    end

    %agrego la frecuencia de la palabra a la fijacion
    if ~isfield(FIX,'freq')         || RECALCULA.todo  || RECALCULA.FIX 
        FIX=agrego_frecpal_a_fijacion(FIX);
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial')    
        fprintf('Agrego frecuencia a las fijaciones (en FIX) y guardo %s_expe.mat, t=%gseg\n',suj.filename, toc )               
    end

    %agrego la categoria gramatical de la palabra a la fijacion
    if ~isfield(FIX,'catgram')      || RECALCULA.todo  || RECALCULA.FIX 
        FIX=agrego_catgram_a_fijaciones(FIX);
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial')    
        fprintf('Agrego categoria a las fijaciones (en FIX) y guardo %s_expe.mat, t=%gseg\n',suj.filename, toc )               
    end

    %GUI para eliminar fijaciones que salieron feas, las primeras y/o ultimas de cada pantalla
    if ~exist([suj.expepath,expe.filename '_FIXborradas.mat'],'file')  || RECALCULA.todo  || RECALCULA.FIX || RECALCULA.FIXborradas
        %si ya habia un archivo, lo cargo, sino creo la variable vacia.
        if exist([suj.expepath,expe.filename '_FIXborradas.mat'],'file')
            load([suj.expepath,expe.filename '_FIXborradas'])
        else
            FIXborradas=FIX(1);
            FIXborradas(1:end)=[];
        end            
        
        [FIX FIXborradas]=descartando_fijaciones_erroneas(pantallas, FIX, trial,FIXborradas);
        save([suj.expepath,expe.filename '_FIXborradas'],'FIXborradas')
        fprintf('Fijaciones borradas y guardadas en %s_FIXborradas.mat, t=%gseg\n',suj.filename, toc )                       
        
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial')    
        fprintf('Guardo todo con las FIX removidas en %s_expe.mat, t=%gseg\n',suj.filename, toc )                       
    end    

    %arma estructura palabras
    if ~exist('palabras','var')  || RECALCULA.todo   ||  RECALCULA.FIX || RECALCULA.FIXborradas || RECALCULA.palabras  
        palabras=arma_estructura_palabras(texto,FIX); 
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial','palabras')    
        fprintf('Creo palabras y guardo %s_expe.mat, t=%gseg\n',suj.filename, toc )                               
    end
       
    %agrega lema a palabras
    if 1%~exist('palabras','var')  || RECALCULA.todo   ||  RECALCULA.FIX || RECALCULA.FIXborradas || RECALCULA.palabras  
        palabras=agrega_lema_a_palabras(palabras,suj);
        save([suj.expepath,expe.filename '_expe'],'expe','init','pantallas','texto','FIX','trial','palabras')    
        fprintf('Agrego lema y categoria revisada y guardo %s%s_expe.mat, t=%gseg\n',suj.expepath,suj.filename, toc )                               
    end
    
    
    fprintf('Todas las variables cargadas o calculadas en %2.2f sec.\n',toc)
catch ME
    ME 
    keyboard
end
end

function palabras=agrega_lema_a_palabras(palabras,suj)
try
%cargo palcatN, N es el numero final del sujeto
filename=['palcat' suj.filename(end)];
load(filename)
indpalcat=0;
for i=1:length(palabras)
    %inicializo vacio
    palabras(i).lema='';
    
    %solo miro las palabras que no estan vacias, (por '' o por isempty)
    if strcmp(palabras(i).palabra,'') || isempty(palabras(i).palabra)
        continue        
    else
        indpalcat=indpalcat+1;
    end
    
    % si la palabra es igual, si voy bien..
    if strcmp(palabras(i).palabra,palcat(indpalcat).palabra)
        palabras(i).catgram=palcat(indpalcat).categoria;
        if ~isnan(palabras(i).freq)% si no puse categoria 0, y tiene frecuencia
            palabras(i).freq=palcat(indpalcat).freq;
        else
        end
        palabras(i).lema=palcat(indpalcat).lema;
    else                
        fprintf('En agrega_lema... no coincide la palabra %d: %s con palcat %d: %s\n',i,palabras(i).palabra,indpalcat,palcat(indpalcat).palabra)
%         keyboard
    end
end

% AGREGO LA FRECUENCIA DE LOS LEMAS
    load('C:\Documents and Settings\LNI\Mis documentos\Dropbox\reading\catgram\M_lema.mat')
    [tf loc]=ismember(lower({palabras.palabra}),{M.pal});
    %loc tiene la ubicacion de cada palabra de FIX en la matriz de palabras
    for indpal=1:length(palabras)
        if loc(indpal)>0        
            palabras(indpal).freqlema=M(loc(indpal)).frec;    
        else
            palabras(indpal).freqlema = 1; % suma de las frecuencias de todas las categorias. Inicializamos con 1 para que no hay Inf despues.
        end
    end

catch ME
    ME 
    keyboard
end
end

function palabras   = arma_estructura_palabras(texto,FIX)
    % armo estructura de palabras
    palabras=struct([]);
    for indtexto=1:length(texto)
        for indpal=1:texto(indtexto).numpalabras
            if texto(indtexto).espacioschar(indpal+1)==texto(indtexto).espacioschar(indpal)+1            
                continue
            end
            indnuevapal = length(palabras)+1;
            desde       = texto(indtexto).espacioschar(indpal)+1;
            hasta       = texto(indtexto).espacioschar(indpal+1)-1;
                palabras(indnuevapal).palabrasp = texto(indtexto).texto(desde:hasta);%con SIGNOS de puntuacion
            
            ind         = isletter(palabras(indnuevapal).palabrasp) | ismember(palabras(indnuevapal).palabrasp,'0123456789'); 
                palabras(indnuevapal).palabra   = palabras(indnuevapal).palabrasp(ind);%sin signos de puntuacion
            
            palabras(indnuevapal).finparrafopal = 0;%inicializo con cero, y si es el caso, pongo 1.
            if strcmp(texto(indtexto).texto(1:3),'   ') & indpal==1
                palabras(indnuevapal).inicioparrafopal = 1;
                if indnuevapal>1 
                    palabras(indnuevapal-1).finparrafopal = 1;
                end
            else
                palabras(indnuevapal).inicioparrafopal = 0;
            end
            
            palabras(indnuevapal).renglonG      = indtexto;
            palabras(indnuevapal).WN            = indpal;
            palabras(indnuevapal).idTexto       = texto(indtexto).idTexto;
            palabras(indnuevapal).idClase       = texto(indtexto).idClase;

            palabras(indnuevapal).renglon       = texto(indtexto).renglon; 
            palabras(indnuevapal).pantalla      = texto(indtexto).pantalla;
            palabras(indnuevapal).numpalabras   = texto(indtexto).numpalabras;        
            palabras(indnuevapal).WNG           = texto(indtexto).WNG(indpal);        
            
            palabras(indnuevapal).longpalabra   = length(palabras(indnuevapal).palabra);                

            if ~(isletter(palabras(indnuevapal).palabrasp(end)) | ismember(palabras(indnuevapal).palabrasp(end),'0123456789')); 
                palabras(indnuevapal).simbolo   = palabras(indnuevapal).palabrasp(end);
            else
                palabras(indnuevapal).simbolo   = '';
            end

        end
    end
    palabras(end).finparrafopal = 1;%la ultima tambien termina un parrafo

    palabras    = agrego_catgram_a_fijaciones(palabras);

    palabras    = agrego_frecloc(palabras);

    % asigno las fijaciones que van a cada palabra   
    [tf loc] = ismember([FIX.WNG],[palabras.WNG]);
    for indpal = 1:length(palabras)
        palabras(indpal).FIXs=[];
    end
    for indfix = 1:length(FIX)
        if loc(indfix)>0        
            palabras(loc(indfix)).FIXs = [palabras(loc(indfix)).FIXs indfix];
        end
    end

%     % agrego skip, first pass, gaze a palabras
%     for indpal = 1:length(palabras)
%         palabras(indpal).nFIXs      = length(palabras(indpal).FIXs);
%         palabras(indpal).skip       = 0;
%         palabras(indpal).firstpass  = nan;
%         palabras(indpal).gaze       = nan;
%         if palabras(indpal).nFIXs==0
%             palabras(indpal).skip   = 1;
%         else
%             palabras(indpal).firstpass = FIX(palabras(indpal).FIXs).dur;
%         end
%         if palabras(indpal).nFIXs==1
%             palabras(indpal).gaze   = FIX(palabras(indpal).FIXs).dur;
%         elseif palabras(indpal).nFIXs>1 
%             ind = find(diff(palabras(indpal).FIXs)>1,1,'first');
%                 if ~isempty(ind)            
%                     palabras(indpal).gaze = sum([FIX(palabras(indpal).FIXs(1:ind)).dur]);        
%                 else
%                     palabras(indpal).gaze = sum([FIX(palabras(indpal).FIXs).dur]);        
%                 end
%         end
%     end
    
    % Otra version jk.
%     keyboard
    for indpal = 1:length(palabras)
        fixs = palabras(indpal).FIXs;               %Fijaciones sobre la palabra
        durs = [FIX(palabras(indpal).FIXs).dur];    %Vector de duracion de las fijaciones
        
        palabras(indpal).knFIXs = length(fixs);     %Numero total de fijaciones
        palabras(indpal).kdurs  = [FIX(palabras(indpal).FIXs).dur]; %Vector de duracion de las fix
        palabras(indpal).kpos_c = [FIX(palabras(indpal).FIXs).pos_caracter];
%         palabras(indpal).kposx  = [FIX(palabras(indpal).FIXs).posx]; % No
%         me sirve, quiero las sacadas
        palabras(indpal).kpsacx = nan(size(fixs));
        palabras(indpal).knsacx = nan(size(fixs));
        for indfix=1:length(fixs)
            palabras(indpal).kpsacx(indfix) = FIX(fixs(indfix)).posx - FIX(fixs(indfix)-1).posx;    %Salto fix(n-1)->fix(n)
            palabras(indpal).knsacx(indfix) = FIX(fixs(indfix)+1).posx - FIX(fixs(indfix)).posx;    %Salto fix(n)->fix(n+1)
        end
        
        clus                    = buscar_consecutivos(fixs);    %Cluster de fijaciones consecutivas
        palabras(indpal).knCLUs         = size(clus,1);         %Numero total de clusters en la palabra
        palabras(indpal).kCLUsiz        = diff(clus')+1;        %Tamano de cada cluster (de 1 o mas fijaciones)
        
        palabras(indpal).kskip          = 0;
        
        palabras(indpal).kfirstfix     = nan;
        palabras(indpal).kgaze          = nan;

        palabras(indpal).kpwng          = nan;      %WNG previo
        palabras(indpal).kpren          = nan;      %Renglon previo
        palabras(indpal).kppan          = nan;      %Pantalla previa

        palabras(indpal).knwng          = nan;      %WNG siguiente
        palabras(indpal).knren          = nan;      %Renglon siguiente
        palabras(indpal).knpan          = nan;      %Pantalla siguiente
        
        if (palabras(indpal).knFIXs==0);     
            % Si no hay fijaciones pongo un 1 en SKIP, y despues voy a
            % setear el default de todo el resto, nan probablemente
            palabras(indpal).kskip=1;
            % Igualmente el verdadero SKIP se lo define con las palabras
            % vecinas, viendo si fijo en palabra1 y palabra3, pero no en
            % palabra2.
        else
            % Si hay mas de un cluster viene lo nuevo, tengo que
            % recorrer los clusters
            for indclu = 1:palabras(indpal).knCLUs
                fixs2 = fixs(clus(indclu,1):clus(indclu,2));
                durs2 = durs(clus(indclu,1):clus(indclu,2));
                kpsacx2 = palabras(indpal).kpsacx(clus(indclu,1):clus(indclu,2));
                knsacx2 = palabras(indpal).knsacx(clus(indclu,1):clus(indclu,2));

                % Si hay un solo cluster, es casi como antes
                palabras(indpal).kfirstfix(indclu) = durs2(1);
                palabras(indpal).kgaze(indclu)      = sum(durs2);
                
                palabras(indpal).kpclusacx(indclu)      = kpsacx2(1);
                palabras(indpal).knclusacx(indclu)      = knsacx2(end);

                % La ultima fijacion anterior que no fue WNG=NaN (es decir
                % que fue a una palabra)
                if (fixs2(1)~=1)
                    pre = [FIX(1:fixs2(1)-1).WNG]; 
                    pre = find(~isnan(pre),1,'last');

                    % El numero de {palabra, renglon, pantalla} de esa fijacion
                    if ~isempty(pre)
                        wng = FIX(pre).WNG;
                        ren = FIX(pre).renglon;
                        pan = FIX(pre).pantalla;

                        palabras(indpal).kpwng(indclu)          = wng;
                        palabras(indpal).kpren(indclu)          = ren;
                        palabras(indpal).kppan(indclu)          = pan;
                    end
                end 
                
                
                if (fixs2(end)~=length(FIX))
                    % La siguiente fijacion que no fue WNG=NaN (es decir
                    % que fue a una palabra)
                    nex = [FIX((fixs2(end)+1):end).WNG]; 
                    nex = fixs2(end)+find(~isnan(nex),1,'first');
                    % El numero de {palabra, renglon, pantalla} de esa fijacion
                    if ~isempty(nex)
                        wng = FIX(nex).WNG;
                        ren = FIX(nex).renglon;
                        pan = FIX(nex).pantalla;

                        palabras(indpal).knwng(indclu)          = wng;
                        palabras(indpal).knren(indclu)          = ren;
                        palabras(indpal).knpan(indclu)          = pan;
                    end
                end
            end
        end
    end





    
end

function palabras   = agrego_frecloc(palabras)
    listapalabras   = unique(lower({palabras.palabra}));       %Lista completa de las palabras que aparecen en el texto.
    freqloc         = zeros(length(listapalabras),1);
    %A continuación define frecloc como el número total de veces que
    %aparece cada palabra en el texto.
    for i=1:length(listapalabras); 
        freqloc(i) = sum(strcmp(lower({palabras.palabra}),listapalabras{i})); 
    end
    for indpal=1:length(palabras)
        palabras(indpal).freqloc = freqloc(strcmp(listapalabras,lower(palabras(indpal).palabra)));
    end
end

function FIX        = agrego_catgram_a_fijaciones(FIX)
    % AGREGO CATEGORIA GRAMATICAL A LAS FIJACIONES
%     load('../catgram/M_catgram.mat')
    load('C:\Documents and Settings\LNI\Mis documentos\Dropbox\reading\catgram\M_catgram.mat')
    [tf loc]=ismember(lower({FIX.palabra}),{M.pal});
    %loc tiene la ubicacion de cada palabra de FIX en la matriz de palabras
    for i=1:length(FIX);
        FIX(i).freq = 1; % suma de las frecuencias de todas las categorias. Inicializamos con 1 para que no hay Inf despues.
        FIX(i).catgram='';
        FIX(i).catgramsimple='';
    end
    for indfix=1:length(FIX)
        if loc(indfix)>0        
            FIX(indfix).freq=M(loc(indfix)).frec;    
            FIX(indfix).catgram=M(loc(indfix)).catmax;        
            FIX(indfix).catgramsimple=FIX(indfix).catgram(1);
        end
    end
end

function trial      = agrego_tiempo_ET_a_trial(todo,trial)
disp('Agrego tiempo del ET a trial')
% agrego el tiempo del eyetracker al trial
indini=strmatch('ini',todo.msg);
indend=strmatch('fin',todo.msg);
if length(trial)==length(indini) && length(trial)==length(indend)
    for i=1:length(indini)
        %[A]=sscanf(todo.msg{indini(i)},'inicio%f %f %f');%  %para extraer trial, pantalla y time de cada msg
        trial(i).timeetini=todo.msgtime(indini(i));
        %[A]=sscanf(todo.msg{indend(i)},'fin%f %f %f');%  %para extraer trial, pantalla y time de cada msg
        trial(i).timeetend=todo.msgtime(indend(i));
    end
else
    disp('trial no mide lo mismo que la cantidad de inicios... oops')
end;

end

function expe       = defino_ancho_caracter(expe,texto)% 3- definir ancho del caracter
% expe=rmfield(expe,'anchocaracter')

disp('Defino el ancho del caracter, en pixels')
ancho=nan(1,length(texto));
nchar=nan(1,length(texto));
for indtexto=1:length(texto)
    ancho(indtexto)=diff(texto(indtexto).bbox([1 3]));
    nchar(indtexto)=length(texto(indtexto).texto);
end
figure(5);clf;
plot(nchar,ancho,'.')
xlabel('Nï¿½mero de caracteres')
ylabel('Ancho de la imagen [px]')
lsline
p=polyfit(nchar,ancho,1);    
expe.anchocaracter = p(1);        
expe.anchocaractercorreccion = p(2);            
fprintf('La pendiente es %2.2f (el ancho de cada caracter), la oo es %2.2f\n',expe.anchocaracter,expe.anchocaractercorreccion)
end

function texto      = defino_espacios_en_texto(texto,expe,init)
% 4- definir posicion de los espacios en cada oracion y agrego info de texto (inicio parrafo, renglon)
%texto=rmfield(texto,'espacios');

disp('Defino la posicion de los espacios en cada oracion,')
disp('   y agrego info de texto (inicioparrafopal,espacioschar,renglon,numpalabras,WNG)')
WNG=0;
for indtexto=1:length(texto)
    espacios = strfind(texto(indtexto).texto,' ');
    if strcmp(texto(indtexto).texto(end),' ')%si el ultimo caracter de un renglon es un espacio
        disp(['espacio de mÃ¡s en indtexto=' num2str(indtexto) ': ' texto(indtexto).texto])
        texto(indtexto).texto(end)=[];
        espacios = strfind(texto(indtexto).texto,' ');    
    end
    espacios = [0 espacios length(texto(indtexto).texto)+1];         %#ok<AGROW>
    if strcmp(texto(indtexto).texto(1:3),'   ')%si empieza un parrafo, hay 3 espacios
        espacios = espacios(4:end);
        texto(indtexto).inicioparrafopal = [1 zeros(1,length(espacios)-2)];
%         if strcmp(texto(indtexto-1).texto(end),' ')
%             texto(indtexto-1).texto(end)=[];
%             espacios(end)=[];
%             disp(['espacio de mÃ¡s en indtexto=' num2str(indtexto-1) ])
%         end

        else
        texto(indtexto).inicioparrafopal = zeros(1,length(espacios)-1);
    end
    texto(indtexto).espacioschar = espacios;
    texto(indtexto).espacios = texto(indtexto).bbox(1) + ...        % el inicio del bounding box
                                expe.anchocaractercorreccion + ...  % la correccion por agarrar el bbox un poquin mas grande
                                (espacios-0.5)*expe.anchocaracter;  % el 0.5 es para quedarme en el centro del espacio        
%         figure(1);clf;hold all
%         image(texto(indtexto).imagen)
%         for i=1:length(texto(indtexto).espacios)
%             plot(texto(indtexto).espacios(i)*[1 1]-texto(indtexto).bbox(1),ylim)
%         end
%         axis ij
%         pause

    
%     texto(indtexto).renglon     = %1+mod(indtexto-1,init.MAXLINES);
    texto(indtexto).numpalabras = length(texto(indtexto).inicioparrafopal);

    texto(indtexto).WNG=WNG+(1:texto(indtexto).numpalabras);
    WNG=WNG+texto(indtexto).numpalabras;
end

for idTexto=1:60
    cuales=find([texto.idTexto]==idTexto);
    for j=cuales
        texto(j).renglon=find(cuales==j);
    end
end
end

function FIX        = defino_FIX(todo, trial, expe)
disp('Calculo FIX')
switch expe.ojo
    case 'L'
        lefixrefix='lefix';
    case 'R'
        lefixrefix='refix';
end
% 5- defino FIX, pantalla, renglon, trial, pos, dur
FIX=struct();
for indfix=1:length(todo.(lefixrefix))
    FIX(indfix).tini    = todo.(lefixrefix)(indfix,1);
    FIX(indfix).tfin    = todo.(lefixrefix)(indfix,2);
    FIX(indfix).dur     = todo.(lefixrefix)(indfix,3);
    FIX(indfix).posx    = todo.(lefixrefix)(indfix,4);
    FIX(indfix).posy    = todo.(lefixrefix)(indfix,5);    
    FIX(indfix).renglon = nan;    
    FIX(indfix).trialnum= nan;
    FIX(indfix).pantalla= nan;    
end
for trialnum=1:length(trial)
    tini    = trial(trialnum).timeetini;
    tfin    = trial(trialnum).timeetend;
    indrefix= find(todo.(lefixrefix)(:,1)>tini & todo.(lefixrefix)(:,2)<tfin);
    for i=1:length(indrefix)
        FIX(indrefix(i)).trialnum=trialnum;
        FIX(indrefix(i)).pantalla=trial(trialnum).currentscreen;
    end
    
    if ~isempty(trial(trialnum).renglones)
        [N,BIN]=histc([FIX(indrefix).posy],trial(trialnum).renglones); %#ok<ASGLU>
        for i=1:length(indrefix)
            if ~isnan(FIX(indrefix(i)).pantalla)
                FIX(indrefix(i)).renglon=BIN(i);    
            end    
        end
    else
        disp('No estan definidos los renglones por trial')
    end
    
end
end

function FIX        = asigno_fijaciones_a_palabras(FIX,texto,expe)
disp('Asigno fijaciones a palabras')
try
for indfix=1:length(FIX) %para cada fijacion_ 
    FIX(indfix).WN          = nan; %numero de palabra del renglon
    FIX(indfix).WNG         = nan; %numero de palabra en el texto
    FIX(indfix).numpalabras = nan; %numero de palabras del renglon
    FIX(indfix).palabra     = '';  %la palabra sin signos de puntuacion
    FIX(indfix).palabrasp   = '';  %la palabra con signos de puntuacion
    FIX(indfix).simbolo     = ' '; %si tiene, el simbolo al final
    FIX(indfix).longpalabra = nan; %la longitud de la palabra   
    renglon                 = FIX(indfix).renglon;
    pantalla                = FIX(indfix).pantalla;
    indpantalla=([texto.pantalla]==pantalla);
    if (~isnan(pantalla) && renglon>0 && renglon<=max([texto(indpantalla).renglon]))%si pertenece a alguna pantalla y esta dentro de la region de renglones
        indtexto=find([texto.pantalla]==pantalla & [texto.renglon]==renglon);
        [N,BIN]=histc(FIX(indfix).posx,texto(indtexto).espacios);         %#ok<ASGLU>
        if BIN>0 %si esta dentro de algun bin (palabra)
            FIX(indfix).WN          = BIN;  %           
            FIX(indfix).WNG         = texto(indtexto).WNG(BIN);  %           
            caracteres              = (texto(indtexto).espacioschar(BIN)+1):(texto(indtexto).espacioschar(BIN+1)-1);
            FIX(indfix).palabrasp   = texto(indtexto).texto(caracteres);% palabra con signos de puntuacion
            FIX(indfix).numpalabras = texto(indtexto).numpalabras;
            
            % asignar a la fijacion un numero de caracter dentro de la
            % palabra.
            % cortamos las palabras dejando medio espacio antes y medio
            % despues, si la fijacio va a estos espacios se le asigna 0 o
            % longpalabras+1
            pos_ini_palabra = texto(indtexto).espacios(FIX(indfix).WN)+expe.anchocaracter/2;
            
            FIX(indfix).pos_caracter = floor((FIX(indfix).posx - pos_ini_palabra)/expe.anchocaracter);

            ind = isletter(FIX(indfix).palabrasp) | ismember(FIX(indfix).palabrasp,'0123456789');
                FIX(indfix).palabra     = FIX(indfix).palabrasp(ind);       % palabra solita
                FIX(indfix).longpalabra = length(FIX(indfix).palabra);
                if (ind(end)==0)
                    FIX(indfix).simbolo = FIX(indfix).palabrasp(end);       % simbolo al final
                    if ((FIX(indfix).palabrasp(end)=='.') && ...
                                FIX(indfix).WN == texto(indtexto).numpalabras && ...  
                                indtexto ~= length(texto));
                        if (texto(indtexto+1).inicioparrafopal(1)==1)
                            FIX(indfix).simbolo = '#';
                        end
                    end
                elseif (ind(end)==0)
                    FIX(indfix).simbolo = FIX(indfix).palabrasp(1);         % simbolo al ppio
                end        
        end
    end
end
catch ME
    ME
    keyboard
end
end

function FIX        = agrego_frecpal_a_fijacion(FIX)% 7- agrega frecuencia a las palabras de las fijaciones.
disp('Agrego la frecuencia de las palabras a FIX')
t=importdata('Lista palabras y frecuencia Corco2.TXT','\t');
words=cell(1,length(t));
freqs=nan(1,length(t));
for i=1:length(t)
    words{i}=strtrim(t{i}(1:40));
    freqs(i)=str2double(t{i}(42:end));    
end
clear t

palabras=unique({FIX.palabra});
for i=1:length(FIX)
    FIX(i).freq=nan;
end
for indpalabra=1:length(palabras)
    palabra=palabras{indpalabra};
    ind=find(strcmpi(palabra,words));
    if ~isempty(ind)
        Frequency=freqs(ind);
    else
        Frequency=0;
    end
    ind=find(strcmp(palabra,{FIX.palabra}));
    for i=1:length(ind)
        FIX(ind(i)).freq=Frequency;
    end        
end
end

function trial      = defino_renglones(init, pantallas, todo, trial, texto, expe)

h=dibuja_histo_y_todas_las_fix(pantallas, todo, trial, texto,expe);
title('Marque los limites de los renglones, globales')
gi=ginput(init.MAXLINES+1);
t = gi(:,2);
drawnow

trialnum=1;
trial(1).renglones=sort(t,'ascend');
while 1
    dibuja_un_trial_con_renglones(h(2),init, pantallas, todo, trial, expe,trialnum)
    str=sprintf('Trial %d - Screen %d',trialnum,trial(trialnum).currentscreen);
    title({str 'Cliquee a la derecha del subplot para pasar al trial siguiente' ...
           'Cliquee a la izda del subplot para pasar al trial anterior' ...
           'Cliquee dentro para mover una de las lineas'})
    [x y]=ginput(1);
    if x>max(xlim)
        trialnum=trialnum+1;
        if trialnum<=length(trial)
            trial(trialnum).renglones=trial(trialnum-1).renglones;
        else
            disp('llegue al fin')
            break
        end
    elseif x<min(xlim)
        trialnum=max(trialnum-1,1);
    else
        [minmin indrengloncambia]=min(abs(y-trial(trialnum).renglones)); %#ok<ASGLU>
        [x2 y2]=ginput(1); %#ok<ASGLU>
        trial(trialnum).renglones(indrengloncambia)=y2;
        trial(trialnum).renglones=sort(trial(trialnum).renglones,'ascend');
        [y y2]
    end

end


end

function h          = dibuja_histo_y_todas_las_fix(pantallas, todo, trial, texto ,expe)
switch expe.ojo
    case 'L'
        lefixrefix='lefix';
    case 'R'
        lefixrefix='refix';
end

figure(2);
set(gcf,'Position',[10 40 1375 850])
clf
h(1)=axes('Position',[0.1 0.1 0.2 0.8]);
hold on
[y x] = hist(todo.(lefixrefix)(1:end,5),1:1:768);
area(y,x)
for i=1:10
    %plot(xlim,[texto(i).bbox(2) texto(i).bbox(2)],'r-')
    %plot(xlim,[texto(i).bbox(4) texto(i).bbox(4)],'r-')
    plot(xlim,mean([texto(i).bbox(2) texto(i).bbox(4)])*[1 1],'r-')
end
hold off
ylim([50 700])
box on
set(gca,'XDir','reverse')
set(gca,'YDir','reverse')
h(2)=axes('Position',[0.35 0.1 0.6 0.8]);
hold on
image(pantallas(trial(1).currentscreen).imagen)
plot(todo.(lefixrefix)(:,4),todo.(lefixrefix)(:,5),'b.')
hold off
axis ij
xlim([0.5 1024.5])
ylim([50 700])

end

function              dibuja_un_trial_con_renglones(h,init, pantallas, todo, trial, expe,trialnum)
switch expe.ojo
    case 'L'
        lefixrefix='lefix';
    case 'R'
        lefixrefix='refix';
end
set(gcf,'currentaxes',h);cla;hold all

tini=trial(trialnum).timeetini;
tfin=trial(trialnum).timeetend;


image(pantallas(trial(trialnum).currentscreen).imagen)

indrefix=find(todo.(lefixrefix)(:,1)>tini & todo.(lefixrefix)(:,2)<tfin);    

for i=2:length(indrefix)
    plot(todo.(lefixrefix)(indrefix([i-1 i]),4),todo.(lefixrefix)(indrefix([i-1 i]),5),'b')
end
renglones=trial(trialnum).renglones;
[N,BIN]=histc(todo.(lefixrefix)(indrefix,5),renglones); %#ok<ASGLU>
scatter(todo.(lefixrefix)(indrefix,4),todo.(lefixrefix)(indrefix,5),todo.(lefixrefix)(indrefix,3),BIN,'filled')
for i=1:length(renglones)
    plot([1 1024],[renglones(i) renglones(i)],'k--','LineWidth',1);
end
set(gca,'ytick',renglones,'yticklabel',1:length(renglones))
clear i
axis ij
xlim([1 1024])
ylim([1 768])
caxis([0 init.MAXLINES])

colormap(my_alternate_colormap(init.MAXLINES))
end

function out        = my_alternate_colormap(numlines)
%rojo significa que estan por debajo de lo mas bajo o por encima de lo mas alto
out=[[0 0 0];repmat([[1 0 0];[0 0 1]],floor(numlines/2),1)];
if mod(numlines,2) %si el numero de lineas es impar
    out=[out;[1 0 0]];
end  
end

function [FIX FIXborradas]=descartando_fijaciones_erroneas(pantallas, FIX, trial,FIXborradas)
% load([suj(1).crudopath,suj(1).filename]) %tiene init, pantallas, texto y trial
% load([suj(1).crudopath,suj(1).filename '_todo']) 
% 
% disp(['Cargo _todo.mat: ' num2str(toc)])
% 
% load([suj(1).expepath,suj(1).filename '_expe']) 

trialnum=1;
while 1
    [indfix]=dibuja_un_trial_fijaciones_tiempo(pantallas, FIX, trial, trialnum);
    str=sprintf('Trial %d - Screen %d - NFIXborradas: %d',trialnum,trial(trialnum).currentscreen,length(FIXborradas));
    title({str 'Cliquee a la derecha del subplot para pasar al trial siguiente' ...
           'Cliquee a la izda del subplot para pasar al trial anterior' ...
           'Cliquee dentro para mover una de las lineas' ...
           'Click del medio (ruedita) sale'})
           
    %espera a que sueltes el botondel mouse
    buttons=1;
    while any(buttons)
        [xxx yyy buttons]=getmouse;
    end
    
    [x y button]=ginput(1);
    
    if button==2
        choice = questdlg('Desea salir?', ...
            'Salimos...', ...
            'Si','No','No');
        if strmatch(choice,'Si')
            disp('salimos')
            break        
        else
            continue
        end
    end
    
    if x>max(xlim)%si cliqueo a la derecha del eje
        trialnum=trialnum+1;
        if trialnum<=length(trial)
            trial(trialnum).renglones=trial(trialnum-1).renglones;
        else
            disp('llegue al fin')
            break
        end
    elseif x<min(xlim)%si cliqueo a la izquierda del eje
        trialnum=max(trialnum-1,1);
    else%si cliqueo en la figura
         
         dist=sqrt(([FIX(indfix).posx]-x).^2 + ...
                   ([FIX(indfix).posy]-y).^2);
         [minmin indfixelegida]=min(dist);%elijo la mas cercana al click
         plot(FIX(indfix(indfixelegida)).posx,FIX(indfix(indfixelegida)).posy,'wo')                 
         plot(FIX(indfix(indfixelegida)).posx,FIX(indfix(indfixelegida)).posy,'k+')
         
         str=sprintf('Pulse DERECHO para confirmar, y boton izquierdo para deshacer, NFIXborr=%d',length(FIXborradas));
         text(200,50,str)
         [xx yy buttons]=ginput(1);
         if buttons==3
            FIXborradas(end+1)=FIX(indfix(indfixelegida));%la guardo en una estructura nueva
            FIX=remueve_fijacion(FIX,indfix(indfixelegida));%la borro de FIX            
         end
         
         
    end%if
    

end%while
end%funcytion

function FIX        = remueve_fijacion(FIX,indfix)
    FIX(indfix).renglon=nan;
    FIX(indfix).trialnum=nan;
    FIX(indfix).pantalla=nan;
    FIX(indfix).WN=nan;
    FIX(indfix).WNG=nan;
    FIX(indfix).numpalabras=nan;
    FIX(indfix).palabra='';
    FIX(indfix).palabrasp='';
    FIX(indfix).simbolo=' ';
    FIX(indfix).longpalabra=nan;
    FIX(indfix).freq=1;
    FIX(indfix).catgram='';
    FIX(indfix).catgramsimple='';
    FIX(indfix).pos_caracter=[];
end

function [indfix]   = dibuja_un_trial_fijaciones_tiempo(pantallas, FIX, trial, trialnum)



% tini=trial(trialnum).timeetini;
% tfin=trial(trialnum).timeetend;

figure(1);clf;hold all
str=sprintf('Trial %d - Screen %d',trialnum,trial(trialnum).currentscreen);
title(str)
image(pantallas(trial(trialnum).currentscreen).imagen)


indfix=find([FIX.trialnum]==trialnum);% find([FIX.tini]>tini & [FIX.tfin]<tfin);
if ~isempty(indfix)
    for i=2:length(indfix)
        plot([FIX(indfix([i-1 i])).posx],[FIX(indfix([i-1 i])).posy],'b')
    end
    
    scatter([FIX(indfix).posx], ...
            [FIX(indfix).posy], ...
            [FIX(indfix).dur]/3, ...
            [FIX(indfix).tini],  'filled')
end
clear i 

axis ij
xlim([1 1024])
ylim([1 768])
if length(indfix)>1
    caxis([FIX(indfix([1 end])).tini])   
end


end

