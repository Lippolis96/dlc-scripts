function frames = frameSequenceFromVideo(fileName, format, first_frame, last_frame)

    video = VideoReader(fileName);
    init_frame = read(video, first_frame);
    frames_to_read = last_frame - first_frame;
    % initialize to first frame we are interested in
    index_frame = first_frame;  
    frames = [];
    while index_frame < last_frame+1
        frame = read(video, index_frame);
        if isequal(format{1}, 'RGB24')
            frames = cat(3, frames, frame);
        else % grayscale case
            frames = cat(3, frames, frame(:,:,1));
        end
        index_frame = index_frame + 1;
    end
end