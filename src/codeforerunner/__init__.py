from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("codeforerunner")
except PackageNotFoundError:
    __version__ = "0.0.0"  # running from source without install
