%% chequeo a partir de los textos originales
datadir='E:\Dropbox\_LABO\reading\textos\';
%datadir='/home/marting/reading_julia/textos/';
filenames={'1 Carta abierta' ...
    '2 Bienvenido Bob' ...
    '3 axolotl' ...
    '4 SOMBRAS SOBRE VIDRIO ESMERILADO 1' ...
    '4 SOMBRAS SOBRE VIDRIO ESMERILADO 2' ...
    '5 El origen de las especies' ...
    '6 sacks - rebeca' ...
    '7 el loco cansino' ...
    '8 el negro de paris' ...
    '9 carta a una senorita en paris' ...
    };
tic
for indfile=1:length(filenames)
        filename=filenames{indfile};
        load([datadir filename]);
        fprintf('Archivo %s cargado (%2.2fsec)\n',filename,toc)
        clf
        
        %busco espacios al final de cada renglon
        for indtexto=1:length(texto)
            if isspace(texto(indtexto).texto(end))
                fprintf('\tHay un espacio al final del renglon %d: %s\n',indtexto,texto(indtexto).texto)
            end
        end


    %busco palabras que sean solo simbolos, sin letras ni numeros
    for indtexto=1:length(texto)
        remain=texto(indtexto).texto;
        while ~isempty(remain)
            [token remain]=strtok(remain);
            ind = isletter(token) | ismember(token,'0123456789');
            %token
            if ~any(ind)
                fprintf('\tHay palabras sin letras: %d %s ... %s\n',indtexto, token,texto(indtexto).texto)
            end
        end
    end
    
    %busco espacios dobles en el texto
    for indtexto=1:length(texto)
    	espaciosdobles = strfind(texto(indtexto).texto,'  ');
    	indspace=1;
    	while indspace<=length(espaciosdobles)
    		if espaciosdobles(indspace)==1 && espaciosdobles(2)==2 %Descarto los comienzos de un parrafo
    			indspace=indspace+2;
    		else
    			fprintf('\tHay espacios dobles: %d - %d... %s\n',indtexto,espaciosdobles(indspace),texto(indtexto).texto)
    			indspace=indspace+1;
    		end
    	end
    end
end
%% chequeo textos a partir de los EXPE (a esta altura ya arregle algunas cosas, y las tengo que ver en los textos originales)
datadir='/home/marting/reading_julia/data_expe/';

datadir='E:\Dropbox\_LABO\reading\data_expe/';
d=dir([datadir '*expe.mat']);

filenames={'1 Carta abierta' '2 Bienvenido Bob' '3 axolotl' '4 SOMBRAS SOBRE VIDRIO ESMERILADO 1' '4 SOMBRAS SOBRE VIDRIO ESMERILADO 2' '5 El origen de las especies' '6 sacks - rebeca'};

try    
    tic
    for indfile=1:length(d)
        filename=d(indfile).name;
        load([datadir filename]);
        indtexto=str2num(filename(end-9));
        fprintf('Archivo %s cargado, %s (%2.2fsec)\n',filename,filenames{indtexto},toc)
        figure(1);clf %para que me actualice la info
        
        %busco palabras que no tienen letras, como comillas o puntos aislados
        errores=isempty({palabras.palabra});
        if length(errores)>1
            disp('   danger, error aca!...')
        end        
        
        %busco palabras terminan con espacio
        for indpal=1:length(palabras)
            if isspace(palabras(indpal).palabrasp(end))
                disp('   danger, error aca!...')
            end
        end
        
%         %listado de palabras con simbolos
%         for indpal=1:length(palabras)
%             if ~strcmp(palabras(indpal).palabrasp,palabras(indpal).palabra)
%                 fprintf('%s ',palabras(indpal).palabrasp)
%             end
%         end
%         fprintf('\n')
    end
catch ME
    ME
    keyboard
end