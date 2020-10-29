# -*- coding: utf-8 -*-

import argparse
import os
from PIL import Image
from re import sub
import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import shutil
import subprocess
import urllib


def get_driver(URL, executable_path):
    '''
    Summary get_driver.
    Load an instance of chrome with the supplied website
    Parameters
    ----------
    URL : str
        Address of the website to scrape
    executable_path : raw str
        Path to the chromedriver.exe executable
    Returns
    -------
    driver
        Chromedriver object that will be used for scraping source code
    '''
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--test-type")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(URL)
    return driver


def scrape_img_tag(driver, max_images, brand, brand_dir, term):
    '''
    Summary scrape_img_tag.
    Function that will scrape all images from the img tag of the supplied driver
    Parameters
    ----------
    driver
        Chromedriver object that will be used for scraping source code
    max_images : int
        The max number of images that will be scraped and downloaded
    brand : str
        The brand name of the compnay whose logo is being searched for
    brand_dir : raw str
        The path to the folder that will be used to store the logos belonging to said company
    term : str
        The term that will be entered into Google Images and searched for
    '''
    i = 0
    if not os.path.exists(brand_dir):
        os.makedirs(brand_dir)
    driver = driver.find_elements_by_class_name("mJxzWe")
    for item in driver:
        images = item.find_elements_by_tag_name('img')
        for image in images:
            try:
                if i < max_images:
                    src = image.get_attribute('src')
                    if src is None:
                        data_src = image.get_attribute('data-src')
                        if data_src is not None:
                            print(data_src)
                            print('\n')
                            print('----------NEXT----------')
                            print('\n')
                            filename = brand + '_' + str(i) + '.png'
                            r = requests.get(data_src, stream=True, headers={'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                                                                            "Chrome/43.0.2357.134 Safari/537.36"})
                            if r.status_code == 200:
                                file_path = os.path.join(brand_dir, filename)
                                with open(file_path, 'wb') as f:
                                    r.raw.decode_content = True
                                    shutil.copyfileobj(r.raw, f)
                                    i += 1
                        elif data_src is None:
                            raise Exception("\nNo 'src' or 'data-src' tag found in current element. Moving onto next element ...\n")
                    else:
                        print(src)
                        print('\n')
                        print('----------NEXT----------')
                        print('\n')
                        filename = brand + '_' + str(i) + '.png'
                        file_path = os.path.join(brand_dir, filename)
                        urllib.request.urlretrieve(src, file_path)
                        i += 1
                else:
                    return
            except:
                continue


def png_to_jpg(brand, brand_dir, max_images):
    '''
    Summary png_to_jpg.
    Converts all images in the supplied directory from .png to .jpg
    Parameters
    ----------
    brand : str
        The brand name of the compnay whose logo is being searched for
    brand_dir : raw str
        The path to the folder that will be used to store the logos belonging to said company
    max_images : int
        The max number of images that will be scraped and downloaded
    '''
    i = max_images
    for subdir, dirs, files in os.walk(brand_dir):
        for file in files:
            if '.png' in file:
                filepath = subdir + os.sep + file
                im = Image.open(filepath)
                # Tries to convert the png to a jpg with grey background IF the png file contains a transparent/alpha channel
                try:
                    im.load()
                    rgb_im = Image.new("RGB", im.size, (175, 175, 175))
                    rgb_im.paste(im, mask=im.split()[3]) # 3 is the alpha channel
                # Execute except block if the png doesn't contain a transparent/alpah channel
                except:
                    rgb_im = im.convert('RGB')
                rgb_name = brand + '_' + str(i) + '.jpg'
                save_path = os.path.join(brand_dir, rgb_name)
                while os.path.exists(save_path):
                    i += 1
                    rgb_name = brand + '_' + str(i) + '.jpg'
                    save_path = os.path.join(brand_dir, rgb_name)
                rgb_im.save(save_path, 'JPEG', quality=80)
                i += 1


def clean(brand_dir):
    '''
    Summary clean.
    Remove .png files, keep .jpg files using windows cmd. May have to change command depending on the OS of the host machine
    Parameters
    ----------
    brand_dir : raw str
        The path to the folder that will be used to store the logos belonging to said company
    '''
    temp = os.path.join(brand_dir, '*.png')
    command = 'del /s "' + temp + '"'
    subprocess.run(command, shell=True)


def main():
    parser = argparse.ArgumentParser(description="Scrape images from Google Images")
    parser.add_argument('-m', '--max_images', type=int, help="number of images to scrape, default set to 20, max value allowed is 50", default=20)
    parser.add_argument('-t', '--search_terms', nargs='+', help='terms to search for')
    args = parser.parse_args()
    if not os.path.exists('google_images'):
        os.makedirs('google_images')
    for term in args.search_terms:
        print(f'\nDowloading images for: {term}\n')
        term = term.strip()
        phrase = sub(r"\s+", '+', term)
        brand = sub(r"\s+", '_', term)
        brand_dir = os.path.join('google_images', brand)
        URL = 'https://www.google.com/search?q=' + phrase + '&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjvpO7e0PDqAhUYIDQIHXL9BpgQ_AUoAXoECA4QAw&biw=2276&bih=783&dpr=1.13'
        driver = get_driver(URL, 'chromedriver.exe')
        scrape_img_tag(driver, args.max_images, brand, brand_dir, phrase)
        driver.close()
        png_to_jpg(brand, brand_dir, args.max_images)
        clean(brand_dir)
        print(f'\nFinished downloading images for: {term}\n')
    save_dir = os.path.join(os.getcwd(), 'google_images')
    print(f'\n\nProgram successfully completed. Images are saved in: {save_dir}\n\n')


if __name__ == '__main__':
    main()
