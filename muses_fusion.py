import torch
import argparse
from glob import glob
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--type', type=str, default='0', help='fusion type') # 0: AvgTrim 1: DupTrim 2: Concat
opt = parser.parse_args()

assert(int(opt.type) >= 0 and int(opt.type) <= 2)

files = glob('I3D_RGB/*')
for i in tqdm(files):
	videoFeats = torch.load(i)
	audioFeats = torch.load(i.replace('I3D_RGB', 'AudioFeats'))

	# AvgTrim
	if opt.type == "0":
		k = audioFeats.shape[0] // videoFeats.shape[0]
		combinedFeats = torch.zeros(1, 128)
		for j in range(0, audioFeats.shape[0], 2):
			combinedFeats = torch.cat([combinedFeats, torch.mean(audioFeats[j:j+k, :], 0).unsqueeze(0)], dim=0)
		combinedFeats = combinedFeats[1:, :]
		commonSize = min(combinedFeats.shape[0], videoFeats.shape[0])
		videoFeats = videoFeats[: commonSize, :]
		combinedFeats = combinedFeats[: commonSize, :]
		combinedFeats = torch.cat([videoFeats, combinedFeats], dim=1)
		torch.save(combinedFeats, i.replace('I3D_RGB', 'combinedFeats'))
		continue

	# DupTrim
	if opt.type == "1":
		if audioFeats.shape[0] > videoFeats.shape[0]:
			k = audioFeats.shape[0] // videoFeats.shape[0]
			videoFeats = videoFeats.unsqueeze(1).repeat(1, k, 1)
			videoFeats = videoFeats.reshape(videoFeats.shape[0] * videoFeats.shape[1], videoFeats.shape[2])
		else:
			k = videoFeats.shape[0] // audioFeats.shape[0]
			audioFeats = audioFeats.unsqueeze(1).repeat(1, k, 1)
			audioFeats = audioFeats.reshape(audioFeats.shape[0] * audioFeats.shape[1], audioFeats.shape[2])
			
		commonSize = min(audioFeats.shape[0], videoFeats.shape[0])
		videoFeats = videoFeats[: commonSize, :]
		audioFeats = audioFeats[: commonSize, :]
		combinedFeats = torch.cat([videoFeats, audioFeats], dim=1)
		torch.save(combinedFeats, i.replace('I3D_RGB', 'combinedFeats'))
		continue

	# Concat
	if opt.type == "2":
		combinedFeats = torch.cat([videoFeats, audioFeats], dim=1)
		torch.save(combinedFeats, i.replace('I3D_RGB', 'combinedFeats'))
		continue
