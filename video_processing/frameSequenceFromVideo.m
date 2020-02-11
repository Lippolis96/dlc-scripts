function frames = frameSequenceFromVideo(fileName, first_frame, last_frame)

    video = VideoReader(fileName);
    init_frame = read(video, first_frame);
    frames_to_read = last_frame - first_frame;
    % initialize to first frame we are interested in
    index_frame = first_frame;  
    frames = [];
    while index_frame < last_frame+1
        frame = read(video, index_frame);
        frames = cat(3, frames, frame);
        index_frame = index_frame + 1;
    end
    
end