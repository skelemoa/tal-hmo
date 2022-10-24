import h5py
import torch
import argparse
import numpy as np
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--type', type=str, dest = 'type', default='0', help='fusion type') # 0: AvgTrim 1: DupTrim 2: Concat
parser.add_argument('--vpath', type=str, dest = 'vpath', default='./rgb_val.h5', help='path to visual features')
parser.add_argument('--apath', type=str, dest = 'apath', default='./audio_val.h5', help='path to audio features')
parser.add_argument('--fusedpath', type=str, dest = 'fusedpath', default='./combined_val.h5', help='path to store fused features')
opt = parser.parse_args()

assert(int(opt.type) >= 0 and int(opt.type) <= 2)

vpath = opt.vpath
apath = opt.apath
fused_path = opt.fusedpath

with h5py.File(fused_path, "w") as writeHere:
	with h5py.File(vpath, "r") as rgbF:
		with h5py.File(apath, "r") as AudioF:
			for i in tqdm(rgbF.keys()):
				videoFeats = torch.tensor(np.array(rgbF[i]))
				audioFeats = torch.tensor(np.array(AudioF[i]))

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
					writeHere.create_dataset(i, data=combinedFeats.detach().cpu().numpy())
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
					writeHere.create_dataset(i, data=combinedFeats.detach().cpu().numpy())
					continue

				# Concat
				if opt.type == "2":
					combinedFeats = torch.cat([videoFeats, audioFeats], dim=1)
					writeHere.create_dataset(i, data=combinedFeats.detach().cpu().numpy())
					continue
