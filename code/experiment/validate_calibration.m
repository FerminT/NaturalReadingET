function validate_calibration(window, config, use_eyetracker)
    [firstrowpos, midrowpos, lastrowpos] = get_letters_positions(config);

    xx = [firstrowpos.first(1) firstrowpos.mid(1) firstrowpos.last(1) midrowpos.first(1) midrowpos.mid(1) midrowpos.last(1) ...
        lastrowpos.first(1) lastrowpos.mid(1) lastrowpos.last(1)];
    yy = [firstrowpos.first(2) firstrowpos.mid(2) firstrowpos.last(2) midrowpos.first(2) midrowpos.mid(2) midrowpos.last(2) ...
        lastrowpos.first(2) lastrowpos.mid(2) lastrowpos.last(2)];

    showcentertext(window, 'Mire los puntos que aparecen', config)

    color_green = [0 128 0];
    outercircle_radius = config.charwidth * 2;
    innercircle_radius = fix(outercircle_radius / 3);
    
    for i = 1:length(xx)             
        Screen('FillRect', window, config.backgroundcolor);

        outercircle_pos = [(xx(i) - outercircle_radius) (yy(i) - outercircle_radius) ...
            (xx(i) + outercircle_radius) (yy(i) + outercircle_radius)];       
        innercircle_pos = [(xx(i) - innercircle_radius) (yy(i) - innercircle_radius) ...
            (xx(i) + innercircle_radius) (yy(i) + innercircle_radius)];

        Screen('FillOval', window, config.textcolor, outercircle_pos);
        Screen('FillOval', window, config.backgroundcolor, innercircle_pos);

        t = GetSecs;
        Screen('Flip', window, t + config.ifi); 
        str = ['validation ' num2str(xx(i)) ',' num2str(yy(i))];
        if use_eyetracker && Eyelink('isconnected')
            Eyelink('Message', str)
        end  

        [~, condition] = wait_for_fixation([xx(i) yy(i)], outercircle_radius * 2, ...
            0, use_eyetracker);

        Screen('FillRect', window, config.backgroundcolor);
        Screen('FillOval', window, config.textcolor, outercircle_pos);     
        Screen('FillOval', window, color_green, innercircle_pos);
        
        t = GetSecs;
        Screen('Flip', window, t + config.ifi); 
        if condition == 3 % mouse click
            break
        end
        WaitSecs(0.5);        
    end

    Screen('FillRect', window, config.backgroundcolor);
    Screen('Flip', window); 
end

function [time, condition] = wait_for_fixation(region, size, timeout, use_eyetracker)
    % Condition: 0 -> fixation on region; 1 -> timeout; 2 -> keypress; 3 ->
    % mouse click
    WaitSecs(0.1)
    t0 = GetSecs;
    while 1
        [~, ~, clicks] = GetMouse;
        if max(clicks) > 0
            while any(clicks)
                [~, ~, clicks] = GetMouse;
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
        if use_eyetracker && Eyelink('isconnected')
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
    % Get an estimation of where letter positions will be at the top (first row), mid (mid row),
    % and bottom (last row)
    firstrowpos = struct();
    lastrowpos  = struct();
    midrowpos   = struct();

    firstrowpos.first = [config.leftmargin, config.topmargin];
    firstrowpos.last  = [config.leftmargin + (config.charwidth * config.charwrap), config.topmargin];
    firstrowpos.mid   = [(firstrowpos.first(1) + firstrowpos.last(1)) / 2, (firstrowpos.first(2) + firstrowpos.last(2)) / 2];

    height_offset = config.linespacing * (config.maxlines - 1);

    lastrowpos.first = [firstrowpos.first(1), firstrowpos.first(2) + height_offset];
    lastrowpos.last  = [firstrowpos.last(1), firstrowpos.last(2) + height_offset];
    lastrowpos.mid   = [(lastrowpos.first(1) + lastrowpos.last(1)) / 2, (lastrowpos.first(2) + lastrowpos.last(2)) / 2];

    midrowpos.first = [(firstrowpos.first(1) + lastrowpos.first(1)) / 2, (firstrowpos.first(2) + lastrowpos.first(2)) / 2];
    midrowpos.mid   = [(firstrowpos.mid(1) + lastrowpos.mid(1)) / 2, (firstrowpos.mid(2) + lastrowpos.mid(2)) / 2];
    midrowpos.last  = [(firstrowpos.last(1) + lastrowpos.last(1)) / 2, (firstrowpos.last(2) + lastrowpos.last(2)) / 2];
end