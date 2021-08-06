import requests


class HeliumClient:
    def __init__(self, wallet_address, api_version=None):
        if api_version is None:
            self.api_version = 'v1'
        else:
            self.api_version = api_version
        self.wallet_address = wallet_address
        self.api_endpoint = f'https://api.helium.io/{self.api_version}'
        self.req = requests.Session()
        self.account_hotspots = self.get_account_hotspots()

    def parse_hotspot_returns(self, _hotspot_list):
        all_hotspot_data = []
        for _hotspot in _hotspot_list:
            all_hotspot_data.append(self.parse_hotspot_return(_hotspot))
        return all_hotspot_data

    def parse_hotspot_return(self, _hotspot_data):
        readable_address = f'{_hotspot_data["geocode"]["short_street"]}, ' \
                           f'{_hotspot_data["geocode"]["short_city"]}, ' \
                           f'{_hotspot_data["geocode"]["short_state"]}, ' \
                           f'{_hotspot_data["geocode"]["short_country"]}'

        necessary_hotspot_info = {
            'hotspot_name': _hotspot_data['name'], 'hotspot_address' : _hotspot_data['address'],
            'date_added': _hotspot_data['timestamp_added'],
            'hotspot_status': _hotspot_data['status']['online'],
            'reward_scale': _hotspot_data['reward_scale'], 'address': readable_address,
            'antenna_gain': _hotspot_data['gain'], 'hotspot_elevation': _hotspot_data['elevation']
        }

        return necessary_hotspot_info

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
        hotspot_name = hotspot_name.lower()
        if ' ' in hotspot_name or '_' in hotspot_name:
            hotspot_name = hotspot_name.replace(' ', '-').replace('_', '-')
        _hotspot_return = self.req.get(f'{self.api_endpoint}/hotspots/name/{hotspot_name}')
        if _hotspot_return.status_code < 300:
            return self.parse_hotspot_returns(_hotspot_return.json()['data'])

    def get_hotspots_activity(self, hotspot_addresses=None):
        all_hotspot_activity = []
        if hotspot_addresses is None:
            hotspot_addresses = [ha['hotspot_address'] for ha in self.account_hotspots]
        for _hotspot_addr in hotspot_addresses:
            all_hotspot_activity.append(self.get_hotspot_activity(_hotspot_addr))
        return all_hotspot_activity

    def get_hotspot_activity(self, hotspot_address):
        _hotspot_activity_return = self.req.get(f'{self.api_endpoint}/hotspots/{hotspot_address}/witnesses')
        if _hotspot_activity_return.status_code < 300:
            return _hotspot_activity_return.json()

    def get_hotspots_witnesses(self, hotspot_addresses=None):
        all_hotspot_witnesses = []
        if hotspot_addresses is None:
            hotspot_addresses = [ha['hotspot_address'] for ha in self.account_hotspots]
        for _hotspot_addr in hotspot_addresses:
            all_hotspot_witnesses.append(self.get_hotspot_witnesses(_hotspot_addr))
        return all_hotspot_witnesses

    def get_hotspot_witnesses(self, hotspot_address):
        _hotspot_witness_return = self.req.get(f'{self.api_endpoint}/hotspots/{hotspot_address}/witnesses')
        if _hotspot_witness_return.status_code < 300:
            return _hotspot_witness_return.json()

    def get_hotspots_witnessed(self, hotspot_addresses=None):
        all_hotspot_witnessed = []
        if hotspot_addresses is None:
            hotspot_addresses = [ha['hotspot_address'] for ha in self.account_hotspots]
        for _hotspot_addr in hotspot_addresses:
            all_hotspot_witnessed.append(self.get_hotspot_witnesses(_hotspot_addr))
        return all_hotspot_witnessed

    def get_hotspot_witnessed(self, hotspot_address):
        _hotspot_witnessed_return = self.req.get(f'{self.api_endpoint}/hotspots/{hotspot_address}/witnessed')
        if _hotspot_witnessed_return.status_code < 300:
            return _hotspot_witnessed_return.json()
