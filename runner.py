from pathlib import Path
import yaml
import helium_client
import json

root_dir = Path(__file__).resolve().parent
config_dir = root_dir.joinpath('etc')
data_dir = root_dir.joinpath('data')
activity_file = data_dir.joinpath('activity.json')
if activity_file.exists():
    open(activity_file, 'w').write('')
config_file = config_dir.joinpath('config.yaml')
config = yaml.safe_load(open(config_file))
hel_downloader = helium_client.HeliumClient(config['helium']['wallet_address'])


hotspot_activity = hel_downloader.get_hotspots_activity()

with open(activity_file, 'a') as outfile:
    for a in hotspot_activity:
        for x, y in a.items():
            if y:
                for z in y:
                    json.dump(z, outfile)
                    print(z)
