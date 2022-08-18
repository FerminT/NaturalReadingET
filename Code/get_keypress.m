function [keypressed, time] = get_keypress()
%%% Waits for a keypress and it returns its code alongside the time taken

keyispressed = 0;
t0 = GetSecs;
while keyispressed == 0
    [keyispressed, seconds, keyCode] = KbCheck;
    WaitSecs(0.001);
end
time = seconds - t0;
keypressed = find(keyCode==1);
% Get the first key pressed
keypressed = keypressed(1);
end