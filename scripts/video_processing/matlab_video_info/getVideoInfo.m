function [format, width, height, fps, num_frames] = getVideoInfo(fileName)
   
    v = VideoReader(fileName);
    first_frame = v.readFrame;
    if ~isequal(first_frame(:,:,1),first_frame(:,:,2))
        format = v.VideoFormat;
    else
        format = 'Grayscale';
    end
    
    width = v.Width;
    height = v.Height;
    fps = v.FrameRate;
    count_frames = 1;
    while hasFrame(v)
        count_frames = count_frames+1;
        v.readFrame;
    end
    num_frames = count_frames;
    
end