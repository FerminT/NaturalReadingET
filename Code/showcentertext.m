function showcentertext(screenptr, text, stimuli_config)
    Screen('fillrect', screenptr, stimuli_config.backgroundcolor);
    Screen('TextSize', screenptr, stimuli_config.fontsize);
    Screen('TextFont', screenptr, 'Liberation Serif');

    offset = stimuli_config.charwidth * length(text) / 2;
    DrawFormattedText(screenptr, text, stimuli_config.CX - offset, stimuli_config.CY - 100, stimuli_config.textcolor); 
    Screen('TextSize', screenptr, stimuli_config.fontsize / 2 + 3);
    DrawFormattedText(screenptr, 'Presione una tecla para seguir', stimuli_config.CX - 125, stimuli_config.CY + 50, stimuli_config.textcolor);
    Screen('Flip', screenptr);
    WaitSecs(0.2);
    waitforkeypress();
end

function waitforkeypress()
    while ~KbCheck;WaitSecs(0.001);end
    while KbCheck;end
end