function meanimage_transfer(screens, config)
    I = zeros(size(screens(1).image));
    
    for i = 1:length(screens)    
        I = or(I, screens(i).image == 0);
    end
    
    I = config.backgroundcolor * (1 - I);
    
    imwrite(I,'imagen.bmp');
    
    finfo = imfinfo('imagen.bmp');
    finfo.Filename 
    Eyelink('StopRecording');
    
    transferStatus = Eyelink('ImageTransfer', finfo.Filename, 0, 0, 0, 0, round(config.width/2 - finfo.Width/2), round(config.height/2 - finfo.Height/2), 4);
    if transferStatus ~= 0
        fprintf('Image to host transfer failed\n');
    end
    WaitSecs(0.1);
    Eyelink('StartRecording');
end