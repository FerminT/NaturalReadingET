function palabras   = arma_estructura_palabras(texto)


    texto      = defino_espacios_en_texto(texto);


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

            palabras(indnuevapal).renglon       = texto(indtexto).renglon;        
            palabras(indnuevapal).numpalabras   = texto(indtexto).numpalabras;        
            palabras(indnuevapal).WNG           = texto(indtexto).WNG(indpal);        
            palabras(indnuevapal).pantalla      = texto(indtexto).pantalla;        
            
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
end


function FIX        = agrego_catgram_a_fijaciones(FIX)
    % AGREGO CATEGORIA GRAMATICAL A LAS FIJACIONES
    load('../catgram/M_catgram.mat')
%     load('C:\Documents and Settings\Julia\Dropbox\reading\catgram\M.mat')
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

function texto      = defino_espacios_en_texto(texto)
init.MAXLINES=10;
expe.anchocaracter=14;
expe.anchocaractercorreccion=3;


% 4- definir posicion de los espacios en cada oracion y agrego info de texto (inicio parrafo, renglon)
%texto=rmfield(texto,'espacios');

disp('Defino la posicion de los espacios en cada oracion,')
disp('   y agrego info de texto (inicioparrafopal,espacioschar,renglon,numpalabras,WNG)')
WNG=0;
for indtexto=1:length(texto)
    espacios = strfind(texto(indtexto).texto,' ');
    if strcmp(texto(indtexto).texto(end),' ')%si el ultimo caracter de un renglon es un espacio
        disp(['espacio de más en indtexto=' num2str(indtexto) ': ' texto(indtexto).texto])
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
%             disp(['espacio de más en indtexto=' num2str(indtexto-1) ])
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

    texto(indtexto).renglon     = 1+mod(indtexto-1,init.MAXLINES);
    texto(indtexto).numpalabras = length(texto(indtexto).inicioparrafopal);

    texto(indtexto).WNG=WNG+(1:texto(indtexto).numpalabras);
    WNG=WNG+texto(indtexto).numpalabras;
end
end