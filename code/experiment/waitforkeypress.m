function keypressed = waitforkeypress()    
    while KbCheck;WaitSecs(0.001);end
    keyispressed = 0;
    while keyispressed == 0
        [keyispressed, ~, keyCode] = KbCheck;
        WaitSecs(0.001);
    end
    keypressed = find(keyCode==1);
    % Get the first key pressed
    keypressed = keypressed(1);
end