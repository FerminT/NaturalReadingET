function eyelink_receive_file(edfFile)

% Este es para pedirle el file con la data al eyelink y me lo guarda en la
% carpeta donde lo estoy ejecutando con el nombre que le di en
% eyelink_ini.m
    if EyelinkInit()~= 1; %
    	return;
    end;
    % download data file
    try
        fprintf('Receiving data file ''%s''\n', edfFile );
        status=Eyelink('ReceiveFile',edfFile);
        if status > 0
            fprintf('ReceiveFile status %d\n', status);
        end
        if 2==exist(edfFile, 'file')
            fprintf('Data file ''%s'' can be found in ''%s''\n', edfFile, pwd );
        end
    catch
        fprintf('Problem receiving data file ''%s''\n', edfFile );
    end
    
    % Cierra la comunicacion con el eyelink.
    Eyelink('ShutDown');
end

% el comando basico para recibir cualquier arhivo desde el eyelink es Eyelink('ReceiveFile',nombre del archivo)"