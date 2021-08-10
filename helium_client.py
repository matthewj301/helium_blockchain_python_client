import requests
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level='INFO')

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
        self.account_hotspot_addresses = [ha['hotspot_address'] for ha in self.account_hotspots]
        self.account_hotspot_address_lookup = {ha['hotspot_address']: ha['hotspot_name'] for ha in self.account_hotspots}

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

    def parse_hotspot_activity_return(self, _hotspot_address, _hotspot_activity_data):
        _activity_type = _hotspot_activity_data['type']
        necessary_activity_info = {'activity_type': _activity_type, 'time': _hotspot_activity_data['time'],
                                   'hotspot_name': self.account_hotspot_address_lookup[_hotspot_address]}
        if _activity_type == 'poc_receipts_v1':
            additional_info = _hotspot_activity_data['path'][0]
            if _hotspot_address == additional_info['challengee']:
                necessary_activity_info['challenegee'] = self.account_hotspot_address_lookup[additional_info['challengee']]
            for _possible_witness in _hotspot_activity_data['path'][0]['witnesses']:
                if _possible_witness['gateway'] == _hotspot_address:
                    necessary_activity_info['witness_name'] = self.account_hotspot_address_lookup[_hotspot_address]
                    necessary_activity_info['is_valid'] = _possible_witness['is_valid']
                    necessary_activity_info['snr'] = _possible_witness['snr']
                    necessary_activity_info['signal'] = _possible_witness['signal']
                    necessary_activity_info['channel'] = _possible_witness['channel']
                    if necessary_activity_info['is_valid'] is False:
                        necessary_activity_info['invalid_reason'] = _possible_witness['invalid_reason']
                else:
                    necessary_activity_info['witness_name'] = self.get_hotspot_by_address(_possible_witness['gateway'])
                    necessary_activity_info['is_valid'] = _possible_witness['is_valid']
                    necessary_activity_info['snr'] = _possible_witness['snr']
                    necessary_activity_info['signal'] = _possible_witness['signal']
                    necessary_activity_info['channel'] = _possible_witness['channel']
                    if necessary_activity_info['is_valid'] is False:
                        necessary_activity_info['invalid_reason'] = _possible_witness['invalid_reason']

        elif _activity_type == 'poc_request_v1':
            necessary_activity_info['challenger'] = self.account_hotspot_address_lookup[_hotspot_activity_data['challenger']]
        elif _activity_type == 'rewards_v2':
            for _possible_reward in _hotspot_activity_data['rewards']:
                if _possible_reward['gateway'] == _hotspot_address:
                    necessary_activity_info['type'] = _possible_reward['type']
                    necessary_activity_info['reward_amount'] = _possible_reward['amount']
        else:
            print(_hotspot_activity_data)

        if 'cursor' in _hotspot_activity_data:
            return _hotspot_activity_data

        return necessary_activity_info

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

    def get_hotspot_by_name(self, hotspot_name):
        hotspot_name = hotspot_name.lower()
        if ' ' in hotspot_name or '_' in hotspot_name:
            hotspot_name = hotspot_name.replace(' ', '-').replace('_', '-')
        _hotspot_return = self.req.get(f'{self.api_endpoint}/hotspots/name/{hotspot_name}')
        if _hotspot_return.status_code < 300:
            return self.parse_hotspot_return(_hotspot_return.json()['data'])

    def get_hotspot_by_address(self, hotspot_address):
        _hotspot_return = self.req.get(f'{self.api_endpoint}/hotspots/{hotspot_address}')
        if _hotspot_return.status_code < 300:
            return self.parse_hotspot_return(_hotspot_return.json()['data'])

    def get_hotspots_activity(self, hotspot_addresses=None):
        if hotspot_addresses is None:
            hotspot_addresses = self.account_hotspot_addresses
        for _hotspot_addr in hotspot_addresses:
            _hotspot_dir = {_hotspot_addr: []}
            _hotspot_activity = self.get_hotspot_activity(_hotspot_addr)
            _hotspot_name = self.account_hotspot_address_lookup[_hotspot_addr]
            if _hotspot_activity:
                _relevant_activity = {_hotspot_name: [self.parse_hotspot_activity_return(_hotspot_addr, _a) for _a
                                                      in _hotspot_activity]}
            else:
                _relevant_activity = {_hotspot_name: []}
                logger.debug(f'no data returned for hotspot: {_hotspot_name}')
            yield _relevant_activity

    def get_hotspot_activity(self, hotspot_address):
        _hotspot_activity_return = self.req.get(f'{self.api_endpoint}/hotspots/{hotspot_address}/activity')
        if _hotspot_activity_return.status_code < 300:
            return _hotspot_activity_return.json()['data']

    def get_hotspots_challenges(self, hotspot_addresses=None):
        if hotspot_addresses is None:
            hotspot_addresses = self.account_hotspot_addresses
        for _hotspot_addr in hotspot_addresses:
            yield self.get_hotspot_challenges(_hotspot_addr)

    def get_hotspot_challenges(self, hotspot_address):
        _hotspot_activity_return = self.req.get(f'{self.api_endpoint}/hotspots/{hotspot_address}/challenges')
        if _hotspot_activity_return.status_code < 300:
            return _hotspot_activity_return.json()['data']

    def get_hotspots_witnesses(self, hotspot_addresses=None):
        if hotspot_addresses is None:
            hotspot_addresses = self.account_hotspot_addresses
        for _hotspot_addr in hotspot_addresses:
            yield self.get_hotspot_witnesses(_hotspot_addr)

    def get_hotspot_witnesses(self, hotspot_address):
        _hotspot_witness_return = self.req.get(f'{self.api_endpoint}/hotspots/{hotspot_address}/witnesses')
        if _hotspot_witness_return.status_code < 300:
            return _hotspot_witness_return.json()['data']

    def get_hotspots_witnessed(self, hotspot_addresses=None):
        if hotspot_addresses is None:
            hotspot_addresses = self.account_hotspot_addresses
        for _hotspot_addr in hotspot_addresses:
            yield self.get_hotspot_witnesses(_hotspot_addr)

    def get_hotspot_witnessed(self, hotspot_address):
        _hotspot_witnessed_return = self.req.get(f'{self.api_endpoint}/hotspots/{hotspot_address}/witnessed')
        if _hotspot_witnessed_return.status_code < 300:
            return _hotspot_witnessed_return.json()['data']
