function genero_texto
Screen('Preference', 'SkipSyncTests', 1);
Screen('Preference', 'VisualDebuglevel', 3);% para que no aparezca la pantalla de presentacion
Screen('Preference', 'Verbosity', 1);% para que no muestre los warnings

init.MAXLINES=10;
init.LINESPACING=50;
init.CUANTOWRAP=55;
init.fontsize=18;%aprox 14pixels/char
init.windowrect=[];%[1 1 1024 764]; %si quiero debugear, [] para pantalla completa
init.colorfondo=180;
init.colortexto=0;
init.leftborder=150;
init.topborder=120;

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
try    
    for indfilename=9%:length(filenames)
        clear pantallas
        filename=filenames{indfilename};
        fprintf('Generando %s\n',filename)
        [w init]=inicializa_pantalla(init);
        texto=importa_texto([filename '.txt'],init);
        init.currentline=1;   
        for cont=1:ceil(length(texto)/init.MAXLINES)
            [texto init pantallas(cont)]=dibuja_pantalla_genera_imagenes(w,init,texto,cont);% esto incrementa init.currentline        
        end
        disp('Imagenes generadas')
        sca    
        ListenChar(0)
        
        expe.anchocaractercorreccion=3;
        expe.anchocaracter=14;
        texto      = defino_espacios_en_texto(texto,expe,init);        
        save(filename,'texto','init','pantallas')
    end
catch ME
    sca
    ListenChar(0)
    keyboard
end

end

function [texto init pantalla]=dibuja_pantalla_genera_imagenes(w,init,texto,pantnum)%agrega bbox e imagen a texto
try
    Screen('TextFont',w, 'Courier New');
    Screen('TextSize',w, init.fontsize);
    Screen('TextStyle', w, 1);%0=normal,1=bold,2=italic,4=underline,8=outline,32=condense,64=extend.

    Screen('FillRect', w, init.colorfondo);%fondo blanco
    cont=0;
    init.ultimaslineasdibujadas=[];
    CURRENTLINEINICIAL=init.currentline;
    for indline=1:init.MAXLINES    
        if length(texto)<init.currentline%si quisiera mostrar lineas mas alla del fin del texto        
            init.currentline=CURRENTLINEINICIAL;
            break
        end
        mytext=texto(init.currentline).texto;
        mynumber=num2str(init.currentline);
        [nx, ny, bbox] = DrawFormattedText(w, mytext,  init.leftborder,  init.topborder+cont*init.LINESPACING, init.colortexto);     %#ok<ASGLU>
        %                 DrawFormattedText(w, mynumber,init.leftborder-70, init.topborder+cont*init.LINESPACING, init.colortexto);    
        bbox=bbox+[-1 3 2 8];%left top right bottom, para agarrar todo.
        texto(init.currentline).bbox=bbox;     %Screen('FrameRect', w, 0, bbox);    

        texto(init.currentline).pantalla=pantnum;
        init.ultimaslineasdibujadas=[init.ultimaslineasdibujadas init.currentline];
        init.currentline=init.currentline+1;
        cont=cont+1;
    end
    Screen('Flip',w);
    I=Screen('getimage',w);     
    for i=1:length(init.ultimaslineasdibujadas)
        ind=init.ultimaslineasdibujadas(i);
        bbox=texto(ind).bbox;
        texto(ind).imagen=I(bbox(2):bbox(4),bbox(1):bbox(3),:);
    end
    pantalla.imagen=I;
catch ME
    sca
    ListenChar(0)
    keyboard
end

end

function texto =importa_texto(filename,init)
%importo el texto
texto=importdata(filename);

%lo separo en lineas de hasta CUANTOWRAP caracteres
lineas=[];
for i=1:length(texto)
    texto{i}=WrapString(texto{i},init.CUANTOWRAP);
    temp = regexp(texto{i}, '\n', 'split');
    lineas=[lineas temp]; %#ok<AGROW>
end

%lo convierto en un array de estructuras
texto=struct();
for i=1:length(lineas)
    texto(i).texto=lineas{i};
end    
end

function [w init]=inicializa_pantalla(init)
% inicializa pantalla
try
    screenNumber=max(Screen('Screens'));
    w = Screen('OpenWindow', screenNumber, 0,[50 50 50+1024 50+768], 32, 2);
    Screen(w,'BlendFunction',GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    %Screen('TextFont', w, 'Courier New');
    %Screen('TextSize', w, 20);%ver tama�o
    %HideCursor; %oculta el cursos
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
    keyboard
end
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