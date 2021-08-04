# Compressed Video Generation Example
This is an example to generate compressed video using h264 codec.  
You can test how powerful this codec is.  If things move less in each frames, video will be compressed to tiny size.

## Library
Perhaps, you need to download `OpenH264` library.  
Download it from https://github.com/cisco/openh264/releases .  
Carefully check your error message and find out which version of library is needed.

# How this works?
This will generate 30 seconds duration mp4 video, compressed with H264 codec.  Since each frame doesn't have timestamp to show, 
`timecodes.txt` will be generated to modify with other tools.

# Quick check
Just run this script, `CompressedVideoGenerationExample.py`.