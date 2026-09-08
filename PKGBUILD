pkgname=python-depth-anything-3
_name=depth_anything_3
pkgver=0.1.1
pkgrel=1
pkgdesc="Foundation models for monocular and multi-view depth and geometry estimation"
arch=('any')
url="https://github.com/ByteDance-Seed/Depth-Anything-3"
license=('Apache-2.0')
depends=(
  'pre-commit'
  'python'
  'python-einops'
  'python-fastapi'
  'python-huggingface-hub'
  'python-imageio'
  'python-numpy'
  'python-omegaconf'
  'python-opencv'
  'python-pillow'
  'python-pillow-heif'
  'python-pytorch'
  'python-requests'
  'python-safetensors'
  'python-trimesh'
  'python-typer'
  'python-torchvision'
  'python-xformers'
  'uvicorn'
)
# Upstream pins moviepy==1.0.3, but the AUR only carries MoviePy 2 with a
# different API; only depth_anything_3.utils.export.gs imports it, so it is
# optional rather than a hard dependency.
optdepends=(
  'python-moviepy: video export in depth_anything_3.utils.export.gs'
  'python-plyfile: Gaussian splat export in depth_anything_3.utils.export'
  'python-open3d: mesh evaluation in depth_anything_3.bench'
)
makedepends=(
  'python-build'
  'python-hatchling'
  'python-hatch-vcs'
  'python-installer'
  'python-wheel'
)
# python, python-numpy, python-pytorch, and python-typer are deliberately
# unversioned: the sync repos ship Python 3.14 and NumPy 2, so upstream's
# exact pins (python<=3.13, numpy<2, and similar) can never resolve.
# Dependency review also found no Arch or AUR providers for the required PyPI
# projects evo, e3nn, pycolmap, and lazy_imports, so the runtime dependency
# set remains incomplete.
source=("https://files.pythonhosted.org/packages/6f/41/fae3fc2ceeade5b3e1e711dd5eeed208b2ae0af9b27ad169b0de38558179/${_name}-${pkgver}.tar.gz")
sha256sums=('3aa1daae7d1b7bffa8cffb8c9d9d34839ca0e576b896cb7d7090c4b5e57af72b')

build() {
  cd "${_name}-${pkgver}"
  python -m build --wheel --no-isolation
}

check() {
  cd "${_name}-${pkgver}"
  local test_root="$srcdir/test-root"
  local site_packages
  site_packages=$(python -c 'import site; print(site.getsitepackages()[0])')

  rm -rf "$test_root"
  python -m installer --destdir="$test_root" dist/*.whl

  PYTHONPATH="$test_root$site_packages" python -c \
    'import importlib.util; assert importlib.util.find_spec("depth_anything_3") is not None'
  test -x "$test_root/usr/bin/da3"
  grep -q 'depth_anything_3.cli:app' \
    "$test_root$site_packages/depth_anything_3-$pkgver.dist-info/entry_points.txt"
  test "$(find "$test_root$site_packages/depth_anything_3" -type f \
    \( -name '*.yaml' -o -name '*.yml' \) | wc -l)" -eq 8
  test -f "$test_root$site_packages/depth_anything_3-$pkgver.dist-info/licenses/LICENSE"
}

package() {
  cd "${_name}-${pkgver}"
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
