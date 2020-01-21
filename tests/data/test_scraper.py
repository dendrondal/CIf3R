import os
from PIL import Image
from selenium import webdriver
from pathlib import Path
from src.data.scraper import *

wd = webdriver.Chrome("/home/dal/chromedriver")


def test_fetch_image_urls():
    result = fetch_image_urls("jaberwocky", 5, wd=wd)
    assert len(result) == 5
    assert type(result[0]) == str


def test_hash_urls():
    url_list = ["http://google.com", "http://facebook.com"]
    result = hash_urls(url_list)
    assert len(result) == len(url_list)
    assert list(result.values()[0]) in url_list
    assert type(list(result.values()))[0] == str


def test_pre_prediction_positive():
    prediction_img = Image.open(Path(__file__).parents[1] / "mock_data/R_example.jpg"   )
    true_result = pre_prediction(
        prediction_img, Path(__file__).parents[2] / "models/2019-08-28 08:03:49.h5"
    )
    assert true_result == True


def test_pre_prediction_negative():
    prediction_img = Image.open(Path(__file__).parents[1] / "mock_data/O_example.jpg")
    true_result = pre_prediction(
        prediction_img, Path(__file__).parents[2] / "models/2019-08-28 08:03:49.h5"
    )
    assert true_result == False
