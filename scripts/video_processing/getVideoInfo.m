function [format, width, height, fps, num_frames] = getVideoInfo(fileName)
   
    v = VideoReader(fileName);
    format = v.VideoFormat;
    width = v.Width;
    height = v.Height;
    fps = v.FrameRate;
    count_frames = 0;
    while hasFrame(v)
        count_frames = count_frames+1;
        v.readFrame;
    end
    num_frames = count_frames;
    
end