% Main of the function to 
% 1) read video and get its info
% 2) given frames interval get sequence of frames in between

% read video 
[file, path] = uigetfile;
fileName = fullfile(path,file);

%% get video info
[format, width, height, fps, num_frames] = getVideoInfo(fileName);
format = {format};
video_info = table(format, width, height, fps, num_frames, 'RowNames', {file})
% not matlab converts mp4 and avi file into rgb24

%% frames sequence from video interval
first_frame = 100;
last_frame = 150;
frames = frameSequenceFromVideo(fileName, first_frame, last_frame);
% note: each [n*m*3] matrix is an rgb frame
