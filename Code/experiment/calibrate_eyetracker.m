function calibrate_eyetracker(eyetrackerptr, screens, config)
    Eyelink('StopRecording');    

    EyelinkDoTrackerSetup(eyetrackerptr);
    EyelinkDoDriftCorrection(eyetrackerptr);
    FlushEvents('keydown')

    meanimage_transfer(screens, config);        
    
    Eyelink('StartRecording');     
end