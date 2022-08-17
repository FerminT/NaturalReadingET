%%% This function receives as input texts and outputs the images (i.e.
%%% stimuli) that will be displayed on screen. Additional text information
%%% (position of each word, number of words, etc.) is also stored.

Screen('Preference', 'SkipSyncTests', 1);
Screen('Preference', 'VisualDebuglevel', 3); % remove presentation screen
Screen('Preference', 'Verbosity', 1); % remove warnings

config_file = fullfile('..', 'stimuli_config.mat');
items_path  = fullfile('..', 'Texts');
save_path   = fullfile('..', 'Stimuli');
mkdir(save_path)

files      = dir(items_path);
filenames  = string({files([files.isdir] == 0).name});

load(config_file)

for index = 1:length(filenames)
    try
        clear screens
        filename = filenames(index);
        filepath = fullfile(items_path, filename);
        lines    = import_text_in_lines(filepath, config);
        fprintf('Generating %s\n', filename);

        [screenWindow, config] = initialize_screen(config, 0);
        currentline_index = 1;
        for screenid = 1:ceil(length(lines) / config.maxlines)
            [lines, currentline_index, screens(screenid)] = draw_screen(screenWindow, config, lines, screenid, currentline_index);
        end
        disp('Images created.')
        sca    
        ListenChar(0)
        
        lines = add_text_info(lines, config);        

        save(fullfile(save_path, filename), 'lines', 'screens')
    catch ME
        sca
        disp(getReport(ME))
        ListenChar(0)
        keyboard
    end
end

function text_lines = import_text_in_lines(filename, config)
%%% Import text and divide it into lines according to config.charwrap.
    text = importdata(filename);
    
    lines = [];
    for i = 1:length(text)
        text{i} = WrapString(text{i}, config.charwrap);
        temp    = regexp(text{i}, '\n', 'split');
        lines   = [lines temp]; %#ok<AGROW>
    end
    
    text_lines = struct();
    for i = 1:length(lines)
        text_lines(i).text = lines{i};
    end    
end

function [lines, currentline_index, screen] = draw_screen(screenWindow, config, lines, screenid, currentline_index)
%%% Draw a screen with config.maxlines lines of text. Resolution, text
%%% properties and background color are defined in config.
    try
        Screen('TextFont', screenWindow, config.font);
        Screen('TextSize', screenWindow, config.fontsize);
        Screen('TextStyle', screenWindow, 1); % 0=normal,1=bold,2=italic,4=underline,8=outline,32=condense,64=extend.
        Screen('FillRect', screenWindow, config.backgroundcolor);
        
        counter = 0;
        lastdrawnlines = [];
    
        startingline_index = currentline_index;
        for indline = 1:config.maxlines
            if length(lines) < currentline_index    
                currentline_index = startingline_index;
                break
            end
    
            current_text = lines(currentline_index).text;
            [nx, ny, bbox] = DrawFormattedText(screenWindow, current_text,  config.leftmargin,  ...
                config.topmargin + counter * config.linespacing, config.textcolor);     %#ok<ASGLU>
            
            bbox = bbox + [-1 3 2 8]; % left top right bottom
    
            lines(currentline_index).bbox   = bbox;
            lines(currentline_index).screen = screenid;
    
            lastdrawnlines = [lastdrawnlines currentline_index];
    
            currentline_index = currentline_index + 1;
            counter = counter + 1;
        end
    
        Screen('Flip', screenWindow);
        I = Screen('getimage', screenWindow);  
        screen.image = I;
        
        for i = 1:length(lastdrawnlines)
            ind  = lastdrawnlines(i);
            bbox = lines(ind).bbox;
            lines(ind).image = I(int32(bbox(2)):int32(bbox(4)), int32(bbox(1)):int32(bbox(3)), :);
        end
 
    catch ME
        sca
        disp(getReport(ME))
        ListenChar(0)
        keyboard
    end
end

function lines = add_text_info(lines, config)
% Get where blank spaces are in each line; add some more text info
% (paragraph init, line number).

    WNG = 0;
    for line_index = 1:length(lines)
        spaces = strfind(lines(line_index).text, ' ');
    
        lastChar = lines(line_index).text(end);
        if strcmp(lastChar, ' ')
            disp(['Extra space in line index=' num2str(line_index) ': ' lines(line_index).text])
            lines(line_index).text(end) = [];
            spaces = strfind(lines(line_index).text, ' ');    
        end
    
        spaces = [0 spaces length(lines(line_index).text) + 1];         %#ok<AGROW>
        if strcmp(lines(line_index).text(1:3), '   ') % whenever a paragraph starts, there are three blank spaces
                spaces = spaces(4:end);
                lines(line_index).wordparagraph_init = [1 zeros(1,length(spaces) - 2)];
            else
                lines(line_index).wordparagraph_init = zeros(1, length(spaces) - 1);
        end

        lines(line_index).spaces_index = spaces;
        lines(line_index).spaces_pos   = lines(line_index).bbox(1) + ...     % bounding box starting point
                                        config.charwidthmargin + ...  % some extra margin for the bbox
                                        (spaces - 0.5) * config.charwidth; % 0.5 to land in the middle of it
    
        lines(line_index).linenumber = 1 + mod(line_index - 1, config.maxlines);
        lines(line_index).numwords   = length(lines(line_index).wordparagraph_init);
    
        lines(line_index).WNG = WNG + (1:lines(line_index).numwords);
        WNG = WNG + lines(line_index).numwords;
    end
end