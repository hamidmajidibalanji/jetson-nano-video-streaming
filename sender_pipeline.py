import gi 
gi.require_version('Gst', '1.0')
gi.require_version('GObject', '2.0')

from gi.repository import Gst, GObject  


def sender_pipeline(receiver_ip, port):
	# Initialize the GStreamer
	Gst.init(None)
	pipeline_str = f"""
	nvarguscamerasrc !   # Captures raw frames from the camera modules
	video/x-raw(memory:NVMM), width=1920, height=1080, framerate=30/1 !  # Caps filter
	nvvidconv flip-method=0 !   # converts format/scales and can flip the image.
	video/x-raw, width=960, height=540 ! # downscale to 960*540
	omxh264enc control-rate=2 bitrate=4000000 ! # Hardware accelerated H.264 encoder at ~4 Mbps
	video/x-h264, stream-format=(string)byte-stream ! # Ensures raw H.264 byte‑stream format.
	h264parse ! # Parses the H.264 stream, prepares it for packetization
	rtph264pay mtu=1400 ! # Packetizes into RTP with an MTU of 1400 bytes.
	udpsink host={receiver_ip} port={port} # sends the RTP packets over UDP to the specified IP/port.
	"""

	pipeline = Gst.parse_launch(pipeline_str) # Parses the pipline string and creates a Gstreamer "pipeline" object with the all elements linked as specified.
	pipeline.set_state(Gst.State.PLAYING)  # Tells GStreamer to transition the pipeline into the PLAYING state-start capture, encoding, and packet transmission.

	print("sender pipline started.")  # Logs to the console that streaming has begun.


	try:
		loop = GObject.MainLoop()
		loop.run()

	except KeyboardInterrupt: # Captures the pressing ctrl+C
		print("Stopping sender pipeline.") # Print to the console
		pipeline.set_state(Gst.State.NULL) # Set the pipeline state to "NULL": Stops and frees all resources


if __name__ == "__main__":
	# Replace with the receiver's IP and port.
	sender_pipeline("192.168.43.27", 5000)
	