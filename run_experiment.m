% Constants
SAVE_PATH = 'Data';

[initials, reading_level] = initial_questions();
if isempty(initials); return; end

SAVE_PATH = fullfile(SAVE_PATH, initials);
if exist(SAVE_PATH, 'dir') ~= 7
    mkdir(SAVE_PATH)
end


filename  = fullfile(SAVE_PATH, filenames{idstimuli});

function [initials, reading_level] =  initial_questions()
    prompt = {'Ingrese sus iniciales (incluya segundo nombre, si lo tiene):', ...
        'Del 1 al 10, ¿qué tan frecuente lee?'};
    dlgtitle = 'Información personal';
    dims   = [1 40];
    answer = inputdlg(prompt, dlgtitle, dims);
    if isempty(answer)
        return
    else
        initials = upper(answer{1});
        if length(answer) > 1
            reading_level = answer{2};
        else
            reading_level = 'N/C';
        end
    end
end