from huggingface_hub import snapshot_download


models = {
    "DA3-SMALL": "depth-anything/DA3-SMALL",
    "DA3-BASE": "depth-anything/DA3-BASE",
    "DA3-LARGE": "depth-anything/DA3-LARGE",
    "DA3-GIANT": "depth-anything/DA3-GIANT",
    "DA3NESTED-GIANT-LARGE": "depth-anything/DA3NESTED-GIANT-LARGE",
    "DA3MONO-LARGE": "depth-anything/DA3MONO-LARGE",
    "DA3METRIC-LARGE": "depth-anything/DA3METRIC-LARGE",
    "DA3-LARGE-1.1": "depth-anything/DA3-LARGE-1.1",
    "DA3-GIANT-1.1": "depth-anything/DA3-GIANT-1.1",
    "DA3NESTED-GIANT-LARGE-1.1": "depth-anything/DA3NESTED-GIANT-LARGE-1.1",
}


def download_model(model: str):
    return snapshot_download(models[model.upper()])

