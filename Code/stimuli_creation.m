% function genero_texto
Screen('Preference', 'SkipSyncTests', 1);
Screen('Preference', 'VisualDebuglevel', 3); % para que no aparezca la pantalla de presentacion
Screen('Preference', 'Verbosity', 1); % para que no muestre los warnings

config.maxlines    = 14;
config.linespacing = 55;
config.charwrap    = 99; % right margin: 280 aprox.
config.font        = 'Courier New';
config.fontsize    = 24;
config.windowrect  = [0 0 1920 1080];
config.backgroundcolor = 180;
config.textcolor   = 0;
config.leftmargin  = 280;
config.topmargin   = 185;

items_path = 'Textos';
save_path  = 'Screens';
files      = dir(items_path);
filenames  = string({files([files.isdir] == 0).name});

for index = 1:length(filenames)
    try
        clear pantallas
        filename = filenames(index);
        filepath = fullfile(items_path, filename);
        text     = importa_texto(filepath, config);
        fprintf('Generando %s\n', filename);

        [screenWindow, config] = inicializa_pantalla(config);
        config.currentline = 1;
        for screenid = 1:ceil(length(text) / config.maxlines)
            [text, config, pantallas(screenid)] = dibuja_pantalla_genera_imagenes(screenWindow, config, text, screenid); % esto incrementa init.currentline        
        end
        disp('Imágenes generadas')
        sca    
        ListenChar(0)
        
        charproperties.correctingWidth = 3;
        charproperties.width = 14;
        text = defino_espacios_en_texto(text, charproperties, config);        

        save(fullfile(save_path, filename), 'text', 'config', 'pantallas')
    catch ME
        sca
        disp(getReport(ME))
        ListenChar(0)
        keyboard
    end
end

% end

function text = importa_texto(filename, config)
    % importo el texto
    text = importdata(filename);
    
    % lo separo en líneas de hasta config.charwrap caracteres
    lineas = [];
    for i = 1:length(text)
        text{i} = WrapString(text{i}, config.charwrap);
        temp    = regexp(text{i}, '\n', 'split');
        lineas  = [lineas temp];%#ok<AGROW>
    end
    
    % lo convierto en una estructura donde cada fila es una línea
    text = struct();
    for i = 1:length(lineas)
        text(i).texto = lineas{i};
    end    
end

function [screenWindow, config] = inicializa_pantalla(config)
    % inicializa pantalla
    try
        screenNumber = max(Screen('Screens'));
        screenWindow = Screen('OpenWindow', screenNumber, 0, config.linespacing + config.windowrect, 32, 2);
        % [50 50 50+1024 50+768]
        Screen(screenWindow, 'BlendFunction', GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        % HideCursor; % oculta el cursor
        ListenChar(2) % hace que los keypresses no se vean en matlab editor (ojo hay que habilitarlo al final del programa!)
        disp('Pantalla inicializada')
        
        config.fps = Screen('FrameRate', screenWindow); % frames per second
        config.ifi = 1 / config.fps; % inter-frame interval (no lo hago con getflipinterval porque ese mide y este redondea)
        [config.width, config.height] = Screen('WindowSize', screenWindow);
        config.CX = round(config.width/2);
        config.CY = round(config.height/2);
    catch ME
        Screen('CloseAll')
        % ShowCursor; % muestra el cursor
        ListenChar(0) % vuelve a la normalidad. si no pude ejecutarlo, ctrl+c hace lo mismo
        disp('¡Hubo un error en inicializa_pantalla()!')
        disp(ME)
        keyboard
    end
end

function [texto, config, pantalla] = dibuja_pantalla_genera_imagenes(screenWindow, config, texto, screenid)
% agrega bbox e imagen a texto
try
    Screen('TextFont', screenWindow, config.font);
    Screen('TextSize', screenWindow, config.fontsize);
    Screen('TextStyle', screenWindow, 1); % 0=normal,1=bold,2=italic,4=underline,8=outline,32=condense,64=extend.
    Screen('FillRect', screenWindow, config.backgroundcolor);
    
    contador = 0;
    lastdrawnlines = [];

    startingLine = config.currentline;
    for indline = 1:config.maxlines
        if length(texto) < config.currentline % si quisiera mostrar lineas mas alla del fin del texto        
            config.currentline = startingLine;
            break
        end

        currentText = texto(config.currentline).texto;
        [nx, ny, bbox] = DrawFormattedText(screenWindow, currentText,  config.leftmargin,  ...
            config.topmargin + contador * config.linespacing, config.textcolor);     %#ok<ASGLU>
        bbox = bbox + [-1 3 2 8]; % left top right bottom, para agarrar todo.

        texto(config.currentline).bbox     = bbox;
        texto(config.currentline).pantalla = screenid;

        lastdrawnlines = [lastdrawnlines config.currentline];

        config.currentline = config.currentline + 1;
        contador = contador + 1;
    end

    Screen('Flip', screenWindow);
    I = Screen('getimage', screenWindow);     
    for i = 1:length(lastdrawnlines)
        ind  = lastdrawnlines(i);
        bbox = texto(ind).bbox;
        texto(ind).imagen = I(bbox(2):bbox(4), bbox(1):bbox(3), :);
    end

    pantalla.imagen = I;
catch ME
    sca
    ListenChar(0)
    keyboard
end

end

function text = defino_espacios_en_texto(text, charproperties, config)
% 4- definir posicion de los espacios en cada oracion y agrego info de texto (inicio parrafo, renglon)
%texto=rmfield(texto,'espacios');

    disp('Defino la posición de los espacios en cada oración,')
    disp('   y agrego info de texto (inicioparrafopal, espacioschar, renglon, numpalabras, WNG)')
    WNG=0;
    for indtexto = 1:length(text)
        espacios = strfind(text(indtexto).texto,' ');
    
        lastChar = text(indtexto).texto(end);
        if strcmp(lastChar, ' ')
            disp(['espacio de más en indtexto=' num2str(indtexto) ': ' text(indtexto).texto])
            text(indtexto).texto(end) = [];
            espacios = strfind(text(indtexto).texto,' ');    
        end
    
        espacios = [0 espacios length(text(indtexto).texto) + 1];         %#ok<AGROW>
        if strcmp(text(indtexto).texto(1:3), '   ') % si empieza un parrafo, hay 3 espacios
                espacios = espacios(4:end);
                text(indtexto).inicioparrafopal = [1 zeros(1,length(espacios) - 2)];
            else
                text(indtexto).inicioparrafopal = zeros(1, length(espacios) - 1);
        end
        text(indtexto).espacioschar = espacios;
        text(indtexto).espacios = text(indtexto).bbox(1) + ...        % el inicio del bounding box
                                    charproperties.correctingWidth + ...  % la correccion por agarrar el bbox un poquin mas grande
                                    (espacios - 0.5) * charproperties.width;  % el 0.5 es para quedarme en el centro del espacio        
    
        text(indtexto).renglon     = 1 + mod(indtexto - 1, config.maxlines);
        text(indtexto).numpalabras = length(text(indtexto).inicioparrafopal);
    
        text(indtexto).WNG = WNG + (1:text(indtexto).numpalabras);
        WNG = WNG + text(indtexto).numpalabras;
    end
end