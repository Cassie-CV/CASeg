# CASeg
A novel deep network with triangular-star spatial-spectral fusion encoding and entropy-aware double decoding for coronary artery segmentation

**Framework**
![Cow1](https://github.com/Cassie-CV/CASeg/blob/main/figure/framework.png?raw=true 'Cow1')
The framework of this work offers a visual overview that delineates the entire flow from problem statement to methodology, and experimental setup.

**Quantitative Comparison**
Quantitative comparison with state-of-the-art methods on the CTA119 dataset
and the ASOCA dataset The best results are in bold, and the second-best results are
underlined.
![Cow2](https://github.com/Cassie-CV/CASeg/blob/main/figure/sota.png?raw=true 'Cow2')

**Qualitative Comparison**
![Cow3](https://github.com/Cassie-CV/CASeg/blob/main/figure/SOTA2.png?raw=true 'Cow3')
Qualitative comparison of three typical cases between different methods for
coronary artery segmentation. The yellow and green dashed circles highlight the regions
for better visual comparison.

**Usage**

**Data preparation** Your datasets directory tree should be look like this:

**data**
├── npy
    ├── img
        ├── 1.npy
        ├── 2.npy
        └── ...
    └── mask
        ├── 1.npy
        ├── 2.npy
        └── ...
