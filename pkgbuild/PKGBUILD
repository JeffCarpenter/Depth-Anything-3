# Maintainer: Jeff C <pub@jeffc.ca>
pkgname=python-depth-anything-3-git
_name=depth_anything_3
pkgver=0.1.1.r43.g41ad16c
pkgrel=1
pkgdesc="Foundation models for monocular and multi-view depth and geometry estimation"
arch=('any')
url="https://github.com/JeffCarpenter/Depth-Anything-3"
license=('Apache-2.0')
depends=(
  'python'
  'python-addict'
  'python-einops'
  'python-fastapi'
  'python-huggingface-hub'
  'python-imageio'
  'python-matplotlib'
  'python-numpy'
  'python-omegaconf'
  'python-opencv'
  'python-pillow'
  'python-pillow-heif'
  'python-pydantic'
  'python-pytorch'
  'python-requests'
  'python-scikit-learn'
  'python-scipy'
  'python-safetensors'
  'python-tqdm'
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
  'python-gradio: gradio web app in depth_anything_3.app'
  'python-gsplat: Gaussian splat rendering in depth_anything_3.model.utils.gs_renderer'
  'python-moviepy: video export in depth_anything_3.utils.export.gs'
  'python-plyfile: Gaussian splat export in depth_anything_3.utils.export'
  'python-pycolmap: COLMAP sparse reconstruction export in depth_anything_3.utils.export.colmap'
  'python-e3nn: rotating camera-space SH coefficients in depth_anything_3.utils.sh_helpers'
  'python-evo: Umeyama Sim(3) pose alignment in depth_anything_3.utils.pose_align'
  'python-open3d: mesh evaluation in depth_anything_3.bench'
)
makedepends=(
  'git'
  'python-build'
  'python-hatchling'
  'python-hatch-vcs'
  'python-installer'
  'python-wheel'
)
# python, python-numpy, python-pytorch, and python-typer are deliberately
# unversioned: the sync repos ship Python 3.14 and NumPy 2, so upstream's
# exact pins (python<=3.13, numpy<2, and similar) can never resolve.
# PyPI projects without an Arch or AUR provider (evo, e3nn, pycolmap) are
# optional imports deferred to the call site, so every feature raises a
# clear ImportError naming its dependency; they are carried as optdepends
# for discoverability. The lazy_imports dependency was eliminated entirely
# by that import deferral.
provides=("python-depth-anything-3=${pkgver}")
conflicts=('python-depth-anything-3')
source=("${pkgname}::git+https://github.com/JeffCarpenter/Depth-Anything-3.git")
sha256sums=('SKIP')

pkgver() {
  cd "${pkgname}"
  local describe count hash
  if describe=$(git describe --long --tags 2>/dev/null); then
    printf '%s' "${describe#v}" | sed -e 's/\([^-]*-g\)/r\1/' -e 's/-/./g'
  else
    # No tags on origin yet: fall back to the last PyPI release as the base.
    count=$(git rev-list --count HEAD)
    hash=$(git rev-parse --short HEAD)
    printf '0.1.1.r%s.g%s' "$count" "$hash"
  fi
}

prepare() {
  cd "${pkgname}"
  # hatchling ignores the hatch-vcs version source while project.version is
  # statically pinned to "0.0.0"; declare it dynamic so the wheel metadata
  # carries the real version. No-op once upstream declares it dynamic itself.
  sed -i 's/^version = ".*"/dynamic = ["version"]/' pyproject.toml
  # Fail loudly rather than silently build a 0.0.0 wheel if upstream
  # restructures pyproject.toml so the sed above no longer applies.
  python -c 'import sys, tomllib
proj = tomllib.load(open("pyproject.toml", "rb"))["project"]
if "version" in proj or "version" not in proj.get("dynamic", []):
    sys.exit("prepare(): project.version is not dynamic; the sed failed")'
}

build() {
  cd "${pkgname}"
  # hatch-vcs (setuptools-scm) cannot derive a release base from a tagless
  # clone, so pin the wheel metadata to the pkgver() result restated in PEP
  # 440 form: 0.1.1.r41.g9f0b04b -> 0.1.1+r41.g9f0b04b (wheel metadata must
  # be PEP 440 while $pkgver follows the Arch VCS format; the "+local"
  # spelling sorts newer than the 0.1.1 release and older than 0.1.2,
  # matching the Arch version ordering, unlike the .devN form).
  local scmver
  scmver=$(printf '%s' "${pkgver}" | sed -E 's/\.r([0-9]+)\.g/+r\1.g/')
  export SETUPTOOLS_SCM_PRETEND_VERSION="${scmver}"
  python -m build --wheel --no-isolation
}

check() {
  cd "${pkgname}"
  local test_root="$srcdir/test-root"
  local site_packages scmver
  site_packages=$(python -c 'import site; print(site.getsitepackages()[0])')
  scmver=$(printf '%s' "${pkgver}" | sed -E 's/\.r([0-9]+)\.g/+r\1.g/')
  rm -rf "$test_root"
  python -m installer --destdir="$test_root" dist/*.whl

  PYTHONPATH="$test_root$site_packages" python -c \
    'import importlib.util; assert importlib.util.find_spec("depth_anything_3") is not None'
  test -x "$test_root/usr/bin/da3"
  grep -q 'depth_anything_3.cli:app' \
    "$test_root$site_packages/${_name}"-*.dist-info/entry_points.txt
  # The dist-info metadata must carry the pkgver()-derived PEP 440 version;
  # a 0.0.0 dist-info would mean the version source silently failed.
  test -d "$test_root$site_packages/${_name}-${scmver}.dist-info"
}

package() {
  cd "${pkgname}"
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
