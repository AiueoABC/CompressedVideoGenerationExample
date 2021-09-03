import cv2
import numpy as np


class Frames2Movie:
    def __init__(self, use_nvenc=False):
        self.frames = []  # [(epochTime0, frame0), (epochTime1, frame1), ...]
        self.fps = 10.  # target fps, this example handles a constant framerate video.
        self.codec = 'h264'  # Using h264, to use more efficient codecs, like av1, pls compile opencv from its source.
        self.filename = './video.mp4'
        self.timecodes_filename = './timecodes.txt'
        self._use_nvenc = use_nvenc
        if self._use_nvenc:
            try:
                import ffmpeg
                self._ffmpeg = ffmpeg
            except Exception:
                print('Install ffmpeg-python first => pip install ffmpeg-python')
                self._use_nvenc = False

    def convert2video(self):
        print('Start Encoding')
        height, width = self.frames[0][1].shape[:2]
        _first_timestamp = None
        _time2fill = []
        if self._use_nvenc:
            vcodec = f'{self.codec}_nvenc'
            process = (
                self._ffmpeg
                    .input('pipe:', format='rawvideo', pix_fmt='bgr24', s='{}x{}'.format(width, height))
                    .output(self.filename, pix_fmt='yuv420p', vcodec=vcodec, r=self.fps)
                    .overwrite_output()
                    .run_async(pipe_stdin=True)
            )
            for (_timestamp, _frame) in self.frames:
                process.stdin.write(
                    frame
                        .astype(np.uint8)
                        .tobytes()
                )
                if _first_timestamp is None:
                    _first_timestamp = _timestamp
                    _time2fill.append(0.0)
                else:
                    _time2fill.append(_timestamp - _first_timestamp)
            process.stdin.close()
            process.wait()
        else:
            _codec = cv2.VideoWriter_fourcc(*self.codec)
            _videowriter = cv2.VideoWriter(self.filename, _codec, self.fps, (width, height))
            for (_timestamp, _frame) in self.frames:
                _videowriter.write(_frame)
                if _first_timestamp is None:
                    _first_timestamp = _timestamp
                    _time2fill.append(0.0)
                else:
                    _time2fill.append(_timestamp - _first_timestamp)

            _videowriter.release()
        with open(self.timecodes_filename, 'w') as f:
            # Store timestamp in millis
            f.write('\n'.join([str(int(i * 1000)) for i in _time2fill]))
        print(f'''Finish Encoding:
    Processed Frames: {len(self.frames)}
    Recorded FPS: {self.fps}
    Saved Path: {self.filename}''')


if __name__ == '__main__':
    import time  # to get epochTime
    import threading

    each_video_length = 5  # seconds
    count = 0  # for filename
    target_fps = 60.

    videomaker = Frames2Movie(use_nvenc=True)
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
        videomaker.filename = f'./video_{count}.mp4'
        videomaker.timecodes_filename = f'./timecodes_{count}.txt'

        thread = threading.Thread(target=videomaker.convert2video)
        thread.start()

        count += 1
