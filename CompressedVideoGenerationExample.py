import cv2


class Frames2Movie:
    def __init__(self):
        self.frames = []  # [(epochTime0, frame0), (epochTime1, frame1), ...]
        self.fps = 60.  # target fps, this example handles a constant framerate video.
        self.codec = 'h264'  # Using h264, to use more efficient codecs, like av1, pls compile opencv from its source.
        self.filename = './Video.avi'

    def convert2video(self):
        print('Start Encoding')
        height, width = self.frames[0][1].shape[:2]
        _codec = cv2.VideoWriter_fourcc(*self.codec)
        _videowriter = cv2.VideoWriter(self.filename, _codec, self.fps, (width, height))
        _spf = 1 / self.fps
        _old_frame = ()
        _skipped_frames = 0
        for _frame in self.frames:
            if _old_frame == ():
                _videowriter.write(_frame[1])
                _old_frame = _frame
            else:
                _time2fill = _frame[0] - _old_frame[0]
                if _time2fill >= _spf:
                    _elapsed_time = 0.
                    while _elapsed_time < _time2fill:
                        _elapsed_time += _spf
                        _videowriter.write(_old_frame[1])
                    _old_frame = _frame
                else:  # skipping in case set-fps is not enough for frames
                    _skipped_frames += 1
                    pass
        _videowriter.release()
        print(f'''Finish Encoding:
    Processed Frames: {len(self.frames)}
    Duplicated frames: {_skipped_frames}
    Recorded FPS: {self.fps}
    Saved Path: {self.filename}''')


if __name__ == '__main__':
    import time  # to get epochTime
    import threading

    each_video_length = 30  # seconds
    count = 0  # for filename
    target_fps = 60.

    videomaker = Frames2Movie()
    videomaker.fps = target_fps

    cap = cv2.VideoCapture(0)  # Use camera to get frames
    while True:
        frames = []
        start_time = time.time()
        epochTime = start_time
        print(f"Start Recording #{count}")
        while epochTime - start_time < each_video_length:
            ret, frame = cap.read()
            epochTime = time.time()
            frames.append((epochTime, frame))
        print(f"Finish Recording #{count}")

        videomaker.frames = frames
        videomaker.filename = f'./video_{count}.avi'

        thread = threading.Thread(target=videomaker.convert2video)
        thread.start()

        count += 1
