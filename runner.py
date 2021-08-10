from pathlib import Path
import yaml
import helium_client

root_dir = Path(__file__).resolve().parent
config_dir = root_dir.joinpath('etc')
config_file = config_dir.joinpath('config.yaml')
config = yaml.safe_load(open(config_file))
hel_downloader = helium_client.HeliumClient(config['helium']['wallet_address'])

for a in hel_downloader.get_hotspots_challenges():
    print(a)

#for a in hel_downloader.get_hotspots_activity():
#    for x, y in a.items():
#        if y:
#            for z in y:
#                print(z)

    #    print(x)
# each json event is its own, pull out challenger and challengee