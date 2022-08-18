function [screenWindow, config] = initialize_screen(config, use_eyetracker)
    try
        screenNumber = max(Screen('Screens'));
        screenWindow = Screen('OpenWindow', screenNumber, 0, config.windowrect, 32, 2);
        Screen(screenWindow, 'BlendFunction', GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        ListenChar(2)
        disp('Screen initialized')
        
        config.fps = Screen('FrameRate', screenWindow);
        config.ifi = 1 / config.fps;
        [config.width, config.height] = Screen('WindowSize', screenWindow);
        config.CX = round(config.width/2);
        config.CY = round(config.height/2);
    catch ME
        Screen('CloseAll')
        ListenChar(0)
        disp('An error occurred in initialize_screen!')
        disp(ME)
        if use_eyetracker
            eyelink_end
        end
        keyboard
    end
end