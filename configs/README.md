# Configs Guide

Put versioned experiment configurations here.

This public repo keeps configs in git, while datasets and run outputs remain local and ignored.

Current practice:

- keep one config per experiment family
- keep protocol, split layer, baseline, and dataset explicit in the file
- use JSON while the runtime stays dependency-light

Recommended properties:

- explicit token reduction settings
- explicit communication accounting settings
- explicit split learning cut point
- explicit dataset partition settings
