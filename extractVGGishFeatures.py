import argparse
import os, glob
from numpy import genfromtxt
from pydub import AudioSegment
import numpy as np
import torchaudio
import tensorflow as tf
import tensorflow_hub as hub
import torch

parser = argparse.ArgumentParser(description='Tool to extract audio feature sequence using VGGish')

parser.add_argument(
    '--input',
    default='ActivityNETaudio',
    help='provide the input directory containing audio files (default: ActivityNETaudio)'
)

parser.add_argument(
    '--output',
    default='VGGishFeatures',
    help='path to save VGGish features (default: VGGishFeatures)'
)

parser.add_argument(
    '--snippet_size',
    default=1.2,
    help='snippet size in seconds (default: 1.2)'
)

my_namespace = parser.parse_args()
input_dir = my_namespace.input
output_dir = my_namespace.output

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# VGGish feature extractor model
vggmodel = hub.load('https://tfhub.dev/google/vggish/1')

# Snippet size (In terms of no. of frames).
snippet_size = int(16000 * my_namespace.snippet_size)

data = np.genfromtxt('video_info.csv', delimiter=',', dtype=str)
frames = {}
for i in data[1:]:
	frames[i[0]] = int(i[1])

# Returns feature sequence from audio 'filename'
def getFeature(filename):
	frameCnt = frames[filename.split('.')[0]]
	# Convert m4a to wav
	file = AudioSegment.from_file(input_dir + '/' + filename, "m4a")
	filename = filename.split('.')[0]
	file.export(filename + '.wav', format="wav")

	# Initialize Feature Vector
	featureVec = tf.Variable([[ 0 for i in range(128) ]], dtype='float32')

	# Load audio file as tensor
	audio, sr = torchaudio.load(filename + '.wav')
	# Convert to mono
	audio = audio.mean(axis=0)
	# Resample to 16kHz
	audio = torchaudio.transforms.Resample(sr, 16000)(audio.view(1,-1))[0]

	# Iterate over all snippets and extract feature vector
	pointerr = len(audio) // frameCnt
	frameSize = len(audio) // frameCnt
	for i in range(frameCnt):
		# Get audio segment b/w start_time and end_time
		chunk = audio[max(0, pointerr - (snippet_size // 2)):min(len(audio), pointerr + (snippet_size // 2))]
		if len(chunk) < snippet_size:
			chunk = torch.from_numpy(np.pad(chunk, pad_width=(0, snippet_size - len(chunk)), mode='constant', constant_values=0))
		# Extract feature vector sequence
		feature = vggmodel(chunk)
		# Combine vector sequences by taking mean to represent whole segment. (i.e. convert (Ax128) -> (1x128))
		if len(feature.shape) == 2:
			feature = tf.reduce_mean(feature, axis=0)
		# Concatenate to temporal feature vector sequence
		featureVec = tf.concat([featureVec, [feature]], 0)
		pointerr += frameSize

	# Removing first row with zeroes
	featureVec = featureVec[1:].numpy()

	os.remove(filename + ".wav") 

	# Save as csv
	np.savetxt(output_dir + '/' + filename + ".csv", featureVec, delimiter=",", header=','.join([ 'f' + str(i) for i in range(featureVec.shape[1]) ]))
	print(filename + ' Done')

# Read all files
fileNames = glob.glob(input_dir + "/*")
fileNames = [ os.path.basename(file) for file in fileNames ]
# fileNames.sort()
# fileNames = fileNames[int(len(fileNames) / 2):]
print(str(len(fileNames)) + " files found...")

# Extract temporal feature sequence for all audio files.
for file in fileNames:
	getFeature(file)
