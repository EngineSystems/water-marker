# Water Marker

A simple GUI utility for watermarking one or more folders of images with a PNG watermark.

![](docs/demo.png)


# Installation

Grab a prebuilt binary for your platform at [**Releases**](https://github.com/EngineSystems/water-marker/releases).


# Development

To get started with development, install Python 3.12 on your system.


## Setup

1. Install the following dependencies globally as shown below:

    ```sh
    python -m pip install pipx
    pipx install poetry
    pipx install poe
    pipx install pyinstaller
    pip install pyinstaller-versionfile
    ```

2. Initialize your local development environment using `poetry`:

    ```sh
    poetry install --no-root
    ```

To launch the application during development, run `poetry poe dev`.

# Building an executable for your platform

Use the following script to build an executable for your platform:

```sh
poetry poe package
```
