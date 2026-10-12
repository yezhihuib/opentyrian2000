# Right mechanical four, exact recovered v1

Root approved this generated pilot. Four outputs were recovered byte-for-byte after a workspace reset from the retained generated master and freshly decoded original alpha masks. No regeneration occurred. This package is not yet actual-runtime accepted.

IDs188/189/198/199 form a48x56 logical assembly:188/189 above198/199. Output tiles are192x224 RGBA, density8, logical24x28, anchor0,0. Existing Layer3 NORMAL finite binding only. Do not modify renderer semantics. ID200 and every other material stay unchanged.

Rebuild into a directory that does not exist:

python rebuild.py /absolute/new/output

Python3 and Pillow required. All input hashes are checked; exact decoded RGBA and HDA hashes are enforced. Pillow12.3.0 was used in this recovery. PNG encoder metadata may vary across versions. Fresh separate-directory rebuild verified all four outputs. HDA format is HDR1 plus six little-endian uint32 fields:2010000+sourceID,8,24,28,0,0 followed by RGBA.

The selected imagegen source is resized with Pillow Lanczos to768x896, cropped to192,224,576,672, and assigned exact original opacity support. Its four quadrant crops have no independently generated seams. Source189/199 each have34 transparent logical pixels;188/198 are opaque. Original source RGB is not a build dependency. recover_masks.py documents the independent original-data mask decoding and pins source SHA256.

Fresh neighbor hash proof covers accepted gray123/125/132/133/135/142/143. The original200 insert is excluded. Fresh actual5640 and all-placement context visual review remain integrator gates. Lost pre-reset screenshots are not part of this evidence.
