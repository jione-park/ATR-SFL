# Configs Guide

Put versioned experiment configurations here.

Bootstrap choice:

- the first runnable config is stored as JSON to avoid adding a YAML parser dependency before the training stack stabilizes

Recommended properties:

- one config per experiment family
- explicit token reduction settings
- explicit communication accounting settings
- explicit split learning cut point
- explicit dataset partition settings
