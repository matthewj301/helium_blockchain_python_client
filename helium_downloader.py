import requests

class HeliumDownloader:
    def __init__(self, wallet_address):
        self.wallet_address = wallet_address
        self.api_endpoint = 'https://api.helium.io/v1'
        self.req = requests.Session()


    def parse_hotspot_return(self, _hotspot_data):
        readable_address = f'{_hotspot_data["geocode"]["short_street"]}, ' \
                           f'{_hotspot_data["geocode"]["short_city"]}, ' \
                           f'{_hotspot_data["geocode"]["short_state"]}, ' \
                           f'{_hotspot_data["geocode"]["short_country"]}'

        necessary_hotspot_info = {
            'hotspot_name': _hotspot_data['name'], 'date_added': _hotspot_data['timestamp_added'],
            'hotspot_status': _hotspot_data['status']['online'],
            'reward_scale': _hotspot_data['reward_scale'], 'address': readable_address,
            'antenna_gain': _hotspot_data['gain'], 'hotspot_elevation': _hotspot_data['elevation']
        }

        return necessary_hotspot_info

    def parse_hotspot_returns(self, _hotspot_list):
        all_hotspot_data = []
        for _hotspot in _hotspot_list:
            all_hotspot_data.append(self.parse_hotspot_return(_hotspot))
        return all_hotspot_data

    def get_all_accounts(self):
        _accts_return = self.req.get(f'{self.api_endpoint}/accounts')
        if _accts_return.status_code < 300:
            return _accts_return.json()['data']

    def get_account(self):
        _acct_return = self.req.get(f'{self.api_endpoint}/accounts/{self.wallet_address}')
        if _acct_return.status_code < 300:
            return [_acct_return.json()['data']]

    def get_account_hotspots(self):
        _hotspots_return = self.req.get(f'{self.api_endpoint}/accounts/{self.wallet_address}/hotspots')
        if _hotspots_return.status_code < 300:
            return self.parse_hotspot_returns(_hotspots_return.json()['data'])

    def get_hotspot(self, hotspot_name):
        if ' ' in hotspot_name:
            hotspot_name = hotspot_name.replace(' ', '-')
        _hotspot_return = self.req.get(f'{self.api_endpoint}/hotspots/name/{hotspot_name}')
        if _hotspot_return.status_code < 300:
            return self.parse_hotspot_returns(_hotspot_return.json()['data'])