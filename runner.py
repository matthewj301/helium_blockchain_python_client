from pathlib import Path
import yaml
import helium_downloader

root_dir = Path(__file__).resolve().parent
config_dir = root_dir.joinpath('etc')
config_file = config_dir.joinpath('config.yaml')
config = yaml.safe_load(open(config_file))
hel_downloader = helium_downloader.HeliumDownloader(config['helium']['wallet_address'])


print(hel_downloader.get_account_hotspots())


