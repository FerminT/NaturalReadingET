function validate_calibration(window, config)
    [firstrowpos, midrowpos, lastrowpos] = get_letters_positions(config);

    xx = [firstrowpos.first(1) firstrowpos.mid(1) firstrowpos.last(1) midrowpos.first(1) midrowpos.mid(1) midrowpos.last(1) ...
        lastrowpos.first(1) lastrowpos.mid(1) lastrowpos.last(1)];
    yy = [firstrowpos.first(2) firstrowpos.mid(2) firstrowpos.last(2) midrowpos.first(2) midrowpos.mid(2) midrowpos.last(2) ...
        lastrowpos.first(2) lastrowpos.mid(2) lastrowpos.last(2)];
    
    Screen('FillRect', window, config.backgroundcolor);
    Screen('TextSize', window, 20);
    Screen('DrawText', window, 'Mire los puntos que aparecen', config.CX - 200, config.CY - 100, config.textcolor);
    Screen('DrawText', window, 'Presione una tecla para comenzar', config.CX - 200, config.CY, config.textcolor);

    t = GetSecs;
    Screen('Flip', window, t + config.ifi); 

    waitforkeypress
    WaitSecs(0.5);  
    
    for i = 1:length(xx)             
        Screen('FillRect', window, config.backgroundcolor);

        ssize = 10;
        circle_pos = [xx(i) - ssize yy(i) - ssize xx(i) + ssize yy(i) + ssize];       
        Screen('FillOval', window, config.textcolor, circle_pos);

        ssize = 3;
        circle_pos = [xx(i) - ssize yy(i) - ssize xx(i) + ssize yy(i) + ssize];       
        Screen('FillOval', window, config.backgroundcolor, circle_pos);

        t = GetSecs;
        Screen('Flip', window, t + config.ifi); 
        str = ['pseudocalib ' num2str(xx(i)) ',' num2str(yy(i))];
        if Eyelink('isconnected')
            Eyelink('Message', str)
        end  

        [~, condition] = wait_for_fixation([xx(i) yy(i)], 30, 0);

        Screen('FillRect', window, config.backgroundcolor);

        ssize = 10;
        circle_pos = [xx(i) - ssize yy(i) - ssize xx(i) + ssize yy(i) + ssize];       
        Screen('FillOval', window, config.textcolor, circle_pos);     

        ssize = 3;
        circle_pos = [xx(i) - ssize yy(i) - ssize xx(i) + ssize yy(i) + ssize];       
        Screen('FillOval', window, [0 128 0], circle_pos);
        
        t = GetSecs;
        Screen('Flip', window, t + config.ifi); 
%         if condition == 2 % key press
%             break
%         end
        WaitSecs(0.5);        
    end

    Screen('FillRect', window, config.backgroundcolor);
    Screen('Flip', window); 
end

function [time condition] = wait_for_fixation(region, size, timeout)
    % Condition: 0 -> fixation on region; 1 -> timeout; 2 -> keypress; 3 ->
    % mouse click
    t0 = GetSecs;
    while 1
        [x, y, clicks] = GetMouse;
        if max(clicks) > 0
            while any(clicks)
                [x, y, clicks] = GetMouse;
            end
            condition = 3;
            break             
        end
        if KbCheck
            condition = 2;
            while KbCheck;end
            break 
        end
        if timeout > 0 && GetSecs - t0 < timeout
           condition = 1;
           break
        end
        if Eyelink('isconnected')
            if Eyelink('NewFloatSampleAvailable') > 0
                evt = Eyelink('NewestFloatSample');
                %evt.gx = [posxleft posxright] 
                %evt.gy = [posyleft posyright] 
                %evt.pa = [pupilsize_left pupilsize_right] 
                distleft  = sqrt((evt.gx(1) - region(1))^2 + (evt.gy(1) - region(2))^2);
                distright = sqrt((evt.gx(2) - region(1))^2 + (evt.gy(2) - region(2))^2);            
                if distleft < size || distright < size
                    condition = 0;
                    break
                end
            end
        end
    end
    time = GetSecs - t0;    
end

function [firstrowpos, midrowpos, lastrowpos] = get_letters_positions(config)
    % Get an estimation of where letter positions will be
    firstrowpos = struct();
    lastrowpos  = struct();
    midrowpos = struct();

    firstrowpos.first = [config.leftmargin + config.charwidth / 2, config.topmargin + config.charheight / 2];
    firstrowpos.last = [config.leftmargin + (config.charwidth * config.charwrap) - config.charwidth / 2, config.topmargin + config.charheight / 2];
    firstrowpos.mid  = [(firstrowpos.first(1) + firstrowpos.last(1)) / 2, (firstrowpos.first(2) + firstrowpos.last(2)) / 2];

    height_offset = (config.charheight + config.linespacing) * (config.maxlines - 1);

    lastrowpos.first = [firstrowpos.first(1), height_offset];
    lastrowpos.last  = [firstrowpos.last(1), height_offset];
    lastrowpos.mid   = [(lastrowpos.first(1) + lastrowpos.last(1)) / 2, (lastrowpos.first(2) + lastrowpos.last(2)) / 2];

    midrowpos.first = [(firstrowpos.first(1) + lastrowpos.first(1)) / 2, (firstrowpos.first(2) + lastrowpos.first(2)) / 2];
    midrowpos.mid = [(firstrowpos.mid(1) + lastrowpos.mid(1)) / 2, (firstrowpos.mid(2) + lastrowpos.mid(2)) / 2];
    midrowpos.last = [(firstrowpos.last(1) + lastrowpos.last(1)) / 2, (firstrowpos.last(2) + lastrowpos.last(2)) / 2];
end

function waitforkeypress()
    while ~KbCheck;end
    while KbCheck;end
end