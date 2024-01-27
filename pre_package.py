import pathlib
from packaging.version import Version
import tomllib
import pyinstaller_versionfile

with open("pyproject.toml", "rb") as fp:
    pyproject = tomllib.load(fp)

app_version = pyproject["tool"]["poetry"]["version"]
ver = Version(app_version)

if not (path := pathlib.Path("build/water-marker/")).exists():
    path.mkdir(parents=True)

pyinstaller_versionfile.create_versionfile(
    output_file="build/water-marker/WIN_VERSION.txt",
    version=f"{ver.major}.{ver.minor}.{ver.micro}.0",
    company_name="EngineSystems",
    file_description=pyproject["tool"]["poetry"]["description"],
    internal_name="Water Marker",
    legal_copyright="© Engine Systems 2024-present",
    original_filename="Water Marker.exe",
    product_name="Water Marker",
    translations=[0, 1200]
)

spec = """a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Water Marker {{app_version}}',
    version='dist/WIN_VERSION.txt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
app = BUNDLE(
    exe,
    name=f"Water Marker {{app_version}}.app",
    version='{{app_version}}',
    icon=None,
    bundle_identifier=None,
)
""".replace("{{app_version}}", app_version)

with open("water-marker.spec", "w") as fp:
    fp.write(spec)