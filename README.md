# ti-edge-ai-demos
Demos to show the powerful capabilities of TI Edge AI SDK on J7 platform

# Install the indentation hook

```console
sudo -H pip3 install pre-commit
pip install -e ".[dev]"
```

# Run simple demo example

```console
./main.py -m /opt/edge_ai_apps/models/detection/TFL-OD-200-ssd-mobV1-coco-mlperf-300x300/ -i ../data/0004.jpg -o result.jpg
```