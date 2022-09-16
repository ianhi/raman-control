# raman-control

Control code for the laser components of a custom raman microscope. This probably isn't useful to you except as an example of integrating custom controls with [pymmcore-plus](https://pymmcore-plus.readthedocs.io/en/latest/). This is the core code that interacts with the hardware, for the interface with pymmcore-plus see my [raman-mda-engine](https://github.com/ianhi/raman-mda-engine#raman-mda-engine).


## Installation:
Probably just useful for Ian and Koseki

On linux you can't install `pythonnet` so this won't work. But to make typing easier for developing the mda engine it's an optional dependency.

For a working installation:

`pip install pythonnet`

install the princetoninstruments python library following their instructions. Then do:

`pip install git+https://github.com/ianhi/raman-control`

or

`pip install -e .[full]`

## Basic Usage

```python
from raman_control.spectra import SpectraCollector

# get a singleton object so we don't double initialize
collector = SpectraCollector.instance()


points =  ... # shape 2xN

spec = collector.collect_spectra(points, exposure=500 #msec)
```
