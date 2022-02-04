from src.xkcd_downloader import XkcdDownloader


def main():
    xkcd_downloader_instance = XkcdDownloader()
    xkcd_downloader_instance.make_download()
    print('End of execution')
    print(f'Resume: {xkcd_downloader_instance.get_count_of_comic_downloads}'
          ' comics image files has been downloaded and saved '
          f'in {xkcd_downloader_instance.DIRECTORY}/')


if __name__ == '__main__':
    main()
