import numpy as np
import pytest

from src.preprocessing.image_cleaner import binarize, clean_image, to_grayscale


@pytest.fixture
def sample_image():
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


def test_to_grayscale(sample_image):
    result = to_grayscale(sample_image)
    assert len(result.shape) == 2


def test_binarize(sample_image):
    gray = to_grayscale(sample_image)
    result = binarize(gray, method="otsu")
    assert result.shape == gray.shape
    assert set(np.unique(result)).issubset({0, 255})


def test_clean_image(sample_image):
    result = clean_image(sample_image)
    assert result.dtype == np.uint8