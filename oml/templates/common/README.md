# {{namespace}}


## Quick Start

OML is a command-line tool that makes it easy to manage and
automate the whole machine learning lifecycle. It provides tools for
data scientist to develop, serve and test inferencing code locally.
It is simple - you only need to implement eval() and predict() -
and reusable for many inference platforms.

**Write once. Use many.**

1. Create a new project.
    ```sh
        $ oml init NewModel
    ```
1. Implement `predict()` and `eval()` in `model.py` or `model.cs`
1. Batch scoring with `eval()`
    ```sh
        $ oml eval
    ```
1. Serve the model at localhost. (default: port `8000`)
    ```sh
        $ oml serve
    ```
1. Run unit tests against live model served locally.
    ```sh
        $ oml test -m live -f <unittest.txt>
    ```
1. Create package file for intended serving platform.
    ```sh
        $ oml package
    ```
1. Publish model's latest version to inferencing platform.
    ```sh
        $ oml publish
    ```
