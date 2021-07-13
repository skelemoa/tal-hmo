# AVfusion <span id = "top"></span>

## tal-hmo
Fusional approaches for temporal action localization in untrimmed videos

[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/hear-me-out-fusional-approaches-for-audio/temporal-action-localization-on-thumos14)](https://paperswithcode.com/sota/temporal-action-localization-on-thumos14?p=hear-me-out-fusional-approaches-for-audio)

[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/hear-me-out-fusional-approaches-for-audio/temporal-action-localization-on-activitynet)](https://paperswithcode.com/sota/temporal-action-localization-on-activitynet?p=hear-me-out-fusional-approaches-for-audio)

This repo holds the codes and models for the  framework, introduced in the paper: 

["Hear Me Out: Fusional Approaches for AudioAugmented Temporal Action Localization"](https://arxiv.org/pdf/2106.14118v1.pdf).

# Contents
----
* [Paper Introduction](#intro)
* [Prerequisites](#prerequisites)
* [Data setup](#setup)
* [Download datasets](#data)
* [Training](#train)
* [Testing](#test)
* [Other info](#other)
    * [citation](#cite)
    * [contact](#contact)
----

# Paper Introduction <span id = "intro"> </span>

State  of  the  art  architectures  for  untrimmed  video  Temporal  Action  Localization(TAL)  have  only  considered  RGB  and  Flow  modalities,  leaving  the  information-richaudio  modality  totally  unexploited.   Audio  fusion  has  been  explored  for  the  relatedbut arguably easier problem of trimmed (clip-level) action recognition.  However, TALposes a unique set of challenges.  In this paper, we propose simple but effective fusion-based approaches for TAL. To the best of our knowledge, our work is the first to jointlyconsider audio and video modalities for supervised TAL. We experimentally show thatour schemes consistently improve performance for state of the art video-only TAL ap-proaches.   Specifically,  they  help  achieve  new  state  of  the  art  performance  on  large-scale benchmark datasets - ActivityNet-1.3 (52.73 mAP@0.5) and THUMOS14 (57.18mAP@0.5). Our experiments include ablations involving multiple fusion schemes, modality combinations and TAL architectures.

![Overview](./AVFusion.jpg)

# Prerequisites <span id = "prerequisites"> </span> 

The training and testing in AVFusion is implemented in PyTorch for the ease of use. 

- [PyTorch 1.8.1][pytorch]
                   
Other minor Python modules can be installed by running

```bash
pip install -r requirements.txt
```

 
 

[[back to top](#top)]

### Get the code

Clone this repo with git, **please remember to use --recursive**

```bash
git clone --recursive https://github.com/skelemoa/tal-hmo
```

# Data setup <span id = "setup"> </span>
# Download datasets<span id = "data"> </span>
# Training<span id = "train"> </span>
# Testing<span id = "test"> </span>
# Other info <span id = "other"> </span>
   ### citation<span id = "cite"> </span>
   ### contact<span id = "contact"> </span>
   
   

