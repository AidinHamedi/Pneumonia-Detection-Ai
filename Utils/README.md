# Utils:

## one_cycle_lr and lr_find (by 'benihime91') 
- ### github repo used: [one_cycle_lr-tensorflow](https://github.com/benihime91/one_cycle_lr-tensorflow/tree/master)
  - ### doc link: [1_README.md](docs/1_README.md)

## Python-color-print-V2 and Python-color-print (by Me)
- ### github repo used(Python-color-print-V2): [Python-color-print-V2](https://github.com/Aydinhamedi/Python-color-print-V2)
  - ### doc link: [2_README.md](docs/2_README.md)
- ### github repo used(Python-color-print): [Python-color-print](https://github.com/Aydinhamedi/Python-color-print)
  - ### doc link: [3_README.md](docs/3_README.md)

## P_Debug (by Me)
- ### github repo used: [Python-Debug-print](https://github.com/Aydinhamedi/Python-Debug-print)

## Grad_cam (by GPT-4 😁)

## Other.py (by Me)

## Timeout_input.py (by Me)

## FixedDropout.py (by Me)
For EfficientNet model Example:
```python
from Utils.FixedDropout import FixedDropout
from keras.models import load_model

# Load the model
model = load_model('PAI_model_T.h5', custom_objects={'FixedDropout': FixedDropout})
```
