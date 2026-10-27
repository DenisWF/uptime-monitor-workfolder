import app


def test_package_imports():
    assert app.__version__ == "0.1.0"