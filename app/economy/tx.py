import decimal
import os
import time
from decimal import Decimal
from time import sleep

from django.conf import settings
from django.utils import timezone

import requests
from bs4 import BeautifulSoup
from dashboard.abi import erc20_abi
from dashboard.utils import get_tx_status, get_web3
from economy.models import Token
from hexbytes import HexBytes
from web3 import HTTPProvider, Web3
from web3.exceptions import BadFunctionCallOutput


def maybeprint(_str, _str2=None, _str3=None):
    pass
    #print(_str)

## web3 Exceptions
class TransactionNotFound(Exception):
    """
    Raised when a tx hash used to lookup a tx in a jsonrpc call cannot be found.
    """
    pass

# scrapper settings
ethurl = "https://etherscan.io/tx/"
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
headers = {'User-Agent': user_agent}

 
# ERC20 / ERC721 tokens
# Transfer(address,address,uint256)
# Deposit(address, uint256)
# Approval(address,address, uint256)
SEARCH_METHOD_TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
SEARCH_METHOD_DEPOSIT = '0xaef05ca429cf234724843763035496132d10808feeac94ee79441c83b6dd519a'
SEARCH_METHOD_APPROVAL = '0x7c3bc83eb61feb549a19180bb8de62c55c110922b2a80e511547cf8deda5b25a'

PROVIDER = "wss://mainnet.infura.io/ws/v3/" + settings.INFURA_V3_PROJECT_ID
w3 = Web3(Web3.WebsocketProvider(PROVIDER))
check_transaction = lambda txid: w3.eth.getTransaction(txid)
check_amount = lambda amount: int(amount[75:], 16) if len(amount) == 138 else print (f"{bcolors.FAIL}{bcolors.UNDERLINE} {index_transaction} txid: {transaction_tax[:10]} -> status: 0 False - amount was off by 0.001 {bcolors.ENDC}")
check_token = lambda token_address: len(token_address) == 42
check_contract = lambda token_address, abi : w3.eth.contract(token_address, abi=abi)
check_event_transfer =  lambda contract_address, search, txid : w3.eth.filter({ "address": contract_address, "topics": [search, txid]})
get_decimals = lambda contract : int(contract.functions.decimals().call())

# BulkCheckout parameters
bulk_checkout_address = "0x7d655c57f71464B6f83811C55D84009Cd9f5221C" # same address on mainnet and rinkeby
bulk_checkout_abi = '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"address","name":"dest","type":"address"},{"indexed":true,"internalType":"address","name":"donor","type":"address"}],"name":"DonationSent","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":true,"internalType":"address","name":"dest","type":"address"}],"name":"TokenWithdrawn","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address payable","name":"dest","type":"address"}],"internalType":"struct BulkCheckout.Donation[]","name":"_donations","type":"tuple[]"}],"name":"donate","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"_dest","type":"address"}],"name":"withdrawEther","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_tokenAddress","type":"address"},{"internalType":"address","name":"_dest","type":"address"}],"name":"withdrawToken","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

def getReplacedTX(tx):
    from economy.models import TXUpdate
    txus = TXUpdate.objects.filter(body__hash__iexact=tx)
    for txu in txus:
        replace_hash = txu.body.get('replaceHash')
        if replace_hash:
            return replace_hash
    return None


def transaction_status(transaction, txid):
    """This function is core for check grants transaction list"""
    try:
        contract_address = transaction.to
        contract = check_contract(contract_address, erc20_abi)
        approve_event = check_event_transfer(contract.address, SEARCH_METHOD_APPROVAL, txid)
        transfer_event = check_event_transfer(contract.address, SEARCH_METHOD_TRANSFER, txid)
        deposit_event = check_event_transfer(contract.address, SEARCH_METHOD_DEPOSIT, txid)
        get_symbol = lambda contract: str(contract.functions.symbol().call())
        decimals = get_decimals(contract)
        contract_value = contract.decode_function_input(transaction.input)[1]['_value']
        contract_symbol = get_symbol(contract)
        human_readable_value = Decimal(int(contract_value)) / Decimal(10 ** decimals) if decimals else None
        transfers_web3py = get_token_recipient_senders(recipient_address, dai_address)

        if (transfer_event or deposit_event):
            return {
                'token_amount': human_readable_value,
                'to': '',
                'token_name': contract_symbol,
            }
    except BadFunctionCallOutput as e:
        pass
    except Exception as e:
        maybeprint(89, e)


def check_transaction_contract(transaction_tax):
    transaction = check_transaction(transaction_tax)
    if transaction is not None:
        token_address = check_token(transaction.to)
        if token_address is not False and not token_address == '0x0000000000000000000000000000000000000000':
            return transaction_status(transaction, transaction_tax)


def get_token(token_symbol, network):
    """
    For a given token symbol and amount, returns the token's details. For ETH, we change the 
    token address to 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE since that's the address
    BulkCheckout uses to represent ETH (default here is the zero address)
    """
    token = Token.objects.filter(network=network, symbol=token_symbol, approved=True).first().to_dict
    if token_symbol == 'ETH':
        token['addr'] = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'
    return token

def parse_token_amount(token_symbol, amount, network):
    """
    For a given token symbol and amount, returns the integer version in "wei", i.e. the integer
    form based on the token's number of decimals
    """
    token = get_token(token_symbol, network)
    decimals = token['decimals']
    parsed_amount = int(amount * 10 ** decimals)
    return parsed_amount

def check_for_replaced_tx(tx_hash, network):
    """
    Get status of the provided transaction hash, and look for a replacement transaction hash. If a
    replacement exists, return the status and hash of the new transaction
    """
    status, timestamp = get_tx_status(tx_hash, network, timezone.now())
    if status in ['pending', 'dropped', 'unknown', '']:
        new_tx = getReplacedTX(tx_hash)
        if new_tx:
            tx_hash = new_tx
            status, timestamp = get_tx_status(tx_hash, network, timezone.now())

    return tx_hash, status, timestamp

def is_bulk_checkout_tx(receipt):
    """
    Returns true if the to address of the recipient is the bulk checkout contract
    """
    to_address = receipt['to'].lower()
    is_bulk_checkout = to_address == bulk_checkout_address.lower()
    return is_bulk_checkout

def grants_transaction_validator_v2(contribution, w3):
    """
    This function is used to validate contributions sent on L1 through the BulkCheckout contract.
    This contract can be found here:
      - On GitHub: https://github.com/gitcoinco/BulkTransactions/blob/master/contracts/BulkCheckout.sol
      - On mainnet: https://rinkeby.etherscan.io/address/0x7d655c57f71464b6f83811c55d84009cd9f5221c#code

    To facilitate testing on Rinkeby, we pass in a web3 instance instead of using the mainnet
    instance defined at the top of this file
    """

    # Get bulk checkout contract instance
    bulk_checkout_contract = w3.eth.contract(address=bulk_checkout_address, abi=bulk_checkout_abi)

    # Get specific info about this contribution that we use later
    tx_hash = contribution.split_tx_id
    network = contribution.subscription.network

    # Response that calling function uses to set fields on Contribution
    response = {
        # Set passed to True if matching transfer is found for this contribution. The comment
        # field is used to provide details when false
        'validation': {
            'passed': False,
            'comment': 'Default'
        },
        # Array of addresses where funds were intially sourced from. This is used to detect someone
        # funding many addresses from a single address. This functionality is currently not
        # implemented in grants_transaction_validator_v2 so for now we assume the originator is
        # msg.sender
        'originator': [ '' ],
        # Once tx_cleared is true, the validator is not run again for this contribution
        'tx_cleared': False,
        # True if the checkout transaction was mined
        'split_tx_confirmed': False
    }

    # Return if tx_hash is not valid
    if not tx_hash or len(tx_hash) != 66:
        # Set to true so this doesn't run again, since there's no transaction hash to check
        response['tx_cleared'] = True
        response['validation']['comment'] = 'Invalid transaction hash in split_tx_id'
        return response

    # Check for dropped and replaced txn
    tx_hash, status, timestamp = check_for_replaced_tx(tx_hash, network)

    # If transaction was successful, continue to validate it
    if status == 'success':
        # Transaction was successful so we know it cleared
        response['tx_cleared'] = True 
        response['split_tx_confirmed'] = True 

        # Get the receipt to parse parameters
        receipt = w3.eth.getTransactionReceipt(tx_hash)

        # Validator currently assumes msg.sender == originator
        response['originator'] = [ receipt['from'] ]

        # Return if recipient is not the BulkCheckout contract
        is_bulk_checkout = is_bulk_checkout_tx(receipt)
        if not is_bulk_checkout:
            to_address = receipt['to']
            response['validation']['comment'] = f'This function only validates transactions through the BulkCheckout contract, but this transaction was sent to {to_address}'
            return response

        # Parse receipt logs to look for expected transfer info. We don't need to look at any other
        # receipt parameters because all contributions are emitted as an event
        receipt = w3.eth.getTransactionReceipt(tx_hash)
        parsed_logs = bulk_checkout_contract.events.DonationSent().processReceipt(receipt)

        # Return if no donation logs were found
        if (len(parsed_logs) == 0):
            response['validation']['comment'] = 'No DonationSent events found in this BulkCheckout transaction'
            return response

        # Parse out the transfer details we are looking to find in the event logs
        token_symbol = contribution.normalized_data['token_symbol']
        expected_recipient = contribution.normalized_data['admin_address'].lower()
        expected_token = get_token(token_symbol, network)['addr'].lower() # we compare by token address
        expected_amount = parse_token_amount(
            token_symbol=token_symbol,
            amount=contribution.subscription.amount_per_period_minus_gas_price,
            network=network
        )
        transfer_tolerance = 0.05 # use a 5% tolerance when checking amounts to account for floating point error
        expected_amount_min = int(expected_amount * (1 - transfer_tolerance))
        expected_amount_max = int(expected_amount * (1 + transfer_tolerance))

        # Loop through each event to find one that matches
        for event in parsed_logs:
            is_correct_recipient = event['args']['dest'].lower() == expected_recipient
            is_correct_token = event['args']['token'].lower() == expected_token

            transfer_amount = event['args']['amount']
            is_correct_amount = transfer_amount > expected_amount_min and transfer_amount < expected_amount_max

            if is_correct_recipient and is_correct_token and is_correct_amount:
                # We found the event log corresponding to the contribution parameters
                response['validation']['passed'] = True
                response['validation']['comment'] = 'BulkCheckout. Success'
                return response

        # Transaction was successful, but the expected contribution was not included in the transaction
        response['validation']['comment'] = 'DonationSent event with expected recipient, amount, and token was not found in transaction logs'
        return response

    # If we get here, none of the above failure conditions have been met, so we try to find
    # more information about why it failed
    if status == 'pending':
        response['validation']['comment'] = 'Transaction is still pending'
        return response

    try:
        # Get receipt and set originator to msg.sender
        receipt = w3.eth.getTransactionReceipt(tx_hash)
        response['originator'] = [ receipt['from'] ]

        if receipt.status == 0:
            # Transaction was minded, but 
            response['tx_cleared'] = True
            response['split_tx_confirmed'] = True
            response['validation']['comment'] = 'Transaction failed. See Etherscan for more details'
            return response

        # If here, transaction was successful. This code block should never execute, but it means
        # the transaction was successful but for some reason not parsed above
        raise Exception('Unknown transaction validation flow 1')

    except w3.exceptions.TransactionNotFound:
        response['validation']['comment'] = 'Transaction receipt not found. Transaction may still be pending or was dropped'
        return response

    raise Exception('Unknown transaction validation flow 2')


def grants_transaction_validator(contribution, w3):
    # To facilitate testing on Rinkeby, we pass in a web3 instance instead of using the mainnet
    # instance defined at the top of this file

    tx_list = [contribution.tx_id, contribution.split_tx_id]
    network = contribution.subscription.network

    token_transfer = {}
    txns = []
    validation = {
        'passed': False,
        'comment': 'Default'
    }
    token_originators = []
    amounts = [contribution.subscription.amount_per_period_minus_gas_price, contribution.subscription.amount_per_period]

    for tx in tx_list:

        if not tx:
            continue

        # check for dropped and replaced txn
        status, timestamp = get_tx_status(tx, network, timezone.now())
        maybeprint(120, round(time.time(),2))
        if status in ['pending', 'dropped', 'unknown', '']:
            new_tx = getReplacedTX(tx)
            if new_tx:
                tx = new_tx
                status, timestamp = get_tx_status(tx, network, timezone.now())

        maybeprint(127, round(time.time(),2))
        # check for txfrs
        if status == 'success':

            # check if it was an ETH transaction
            maybeprint(132, round(time.time(),2))
            transaction_receipt = w3.eth.getTransactionReceipt(tx)
            from_address = transaction_receipt['from']
            # todo save back to the txn if needed?
            if (transaction_receipt != None and transaction_receipt.cumulativeGasUsed >= 2100):
                maybeprint(138, round(time.time(),2))
                transaction_hash = transaction_receipt.transactionHash.hex()
                transaction = w3.eth.getTransaction(transaction_hash)
                if transaction.value > 0.001:
                    recipient_address = Web3.toChecksumAddress(contribution.subscription.grant.admin_address)
                    transfer = get_token_originators(recipient_address, '0x0', from_address=from_address, return_what='transfers', tx_id=tx, amounts=amounts)
                    if not transfer:
                        transfer = get_token_originators(recipient_address, '0x0', from_address=from_address, return_what='transfers', tx_id=tx)
                    if transfer:
                        token_transfer = transfer
                maybeprint(148, round(time.time(),2))
                if not token_originators:

                    token_originators = get_token_originators(from_address, '0x0', from_address=None, return_what='originators')

            maybeprint(150, round(time.time(),2))
            # check if it was an ERC20 transaction
            if contribution.subscription.contributor_address and \
                contribution.subscription.grant.admin_address and \
                contribution.subscription.token_address:

                from_address = Web3.toChecksumAddress(contribution.subscription.contributor_address)
                recipient_address = Web3.toChecksumAddress(contribution.subscription.grant.admin_address)
                token_address = Web3.toChecksumAddress(contribution.subscription.token_address)

                maybeprint(160, round(time.time(),2))
                # get token transfers
                if not token_transfer:
                    transfers = get_token_originators(recipient_address, token_address, from_address=from_address, return_what='transfers', tx_id=tx, amounts=amounts)
                    if transfers:
                        token_transfer = transfers
                maybeprint(169, round(time.time(),2))
                if not token_originators:
                    token_originators = get_token_originators(from_address, token_address, from_address=None, return_what='originators')
                maybeprint(170, round(time.time(),2))


        # log transaction and and any xfr
        txns.append({
            'id': tx,
            'status': status,
            })

    if not token_transfer:
        transaction_receipt = w3.eth.getTransactionReceipt(tx)
        is_bulk_checkout = transaction_receipt['to'].lower() == "0x7d655c57f71464B6f83811C55D84009Cd9f5221C".lower()
        if is_bulk_checkout:
            validation['comment'] = "Bulk checkout"
            validation['passed'] = transaction_receipt['status'] == 1
        else:
            validation['comment'] = "No Transfers Occured"
            validation['passed'] = False
    else:
        if token_transfer['token_name'] != contribution.subscription.token_symbol:
            validation['comment'] = f"Tokens do not match, {token_transfer['token_name']} != {contribution.subscription.token_symbol}"
            validation['passed'] = False

            from_address = Web3.toChecksumAddress(contribution.subscription.contributor_address)
            recipient_address = Web3.toChecksumAddress(contribution.subscription.grant.admin_address)
            token_address = Web3.toChecksumAddress(contribution.subscription.token_address)
            _transfers = get_token_originators(recipient_address, token_address, from_address=from_address, return_what='transfers', tx_id=tx, amounts=amounts)
            failsafe = _transfers['token_name'] == contribution.subscription.token_symbol
            if failsafe:
                validation['comment'] = f"Token Transfer Passed on the second try"
                validation['passed'] = True
                token_transfer = _transfers

        else:
            delta1 = float(token_transfer['token_amount_decimal']) - float(contribution.subscription.amount_per_period_minus_gas_price)
            delta2 = float(token_transfer['token_amount_decimal']) - float(contribution.subscription.amount_per_period)
            threshold = float(float(abs(contribution.subscription.amount_per_period_minus_gas_price)) * float(validation_threshold_pct))
            validation['passed'] = (abs(delta1) <= threshold or abs(delta2) <= threshold) or (abs(delta1) <= validation_threshold_total or abs(delta2) <= validation_threshold_total)
            validation['comment'] = f"Transfer Amount is off by {round(delta1, 2)} / {round(delta2, 2)}"


    return {
        'contribution': {
            'pk': contribution.pk,
            'amount_per_period_to_gitcoin': contribution.subscription.amount_per_period_to_gitcoin,
            'amount_per_period_to_grantee': contribution.subscription.amount_per_period_minus_gas_price,
            'from': contribution.subscription.contributor_address,
            'to': contribution.subscription.grant.admin_address,
        },
        'validation': validation,
        'transfers': token_transfer,
        'originator': token_originators,
        'txns': txns,
    }


def trim_null_address(address):
    if address == '0x0000000000000000000000000000000000000000':
        return '0x0'
    else:
        return address


def get_token_recipient_senders(recipient_address, token_address):
    PROVIDER = "wss://mainnet.infura.io/ws/v3/" + settings.INFURA_V3_PROJECT_ID
    w3 = Web3(Web3.WebsocketProvider(PROVIDER))
    contract = w3.eth.contract(
        address=token_address,
        abi=erc20_abi,
    )

    balance = contract.functions.balanceOf(recipient_address).call()

    transfers = contract.events.Transfer.getLogs(
        fromBlock=0,
        toBlock="latest",
        argument_filters={"to": recipient_address})

    return [
        trim_null_address(transfer.args['from'])
        for transfer in transfers
    ]


auth = settings.ALETHIO_KEY
headers = {'Authorization': f'Bearer {auth}'}
validation_threshold_pct = 0.05
validation_threshold_total = 0.05

def get_token_originators(to_address, token, from_address='', return_what='transfers', tx_id='', amounts=[]):
    address = to_address

    #is_address = requests.get('https://api.aleth.io/v1/accounts/' + address, headers=headers).status_code

    #if is_address != requests.codes.ok:
    #    raise ValueError('Address provided is not valid.')

    #is_token = requests.get(
    #    'https://api.aleth.io/v1/tokens/' + (token),
    #    headers=headers
    #).status_code

    #if is_token != requests.codes.ok and token != '0x0':
    #    raise ValueError('Token provided is not valid.')

    #balance = 0
    #try:
        #url = 'https://api.aleth.io/v1/token-balances?filter[account]=' + address + '&filter[token]=' + token
        #balance = requests.get(url, headers=headers).json()['data'][0]['attributes']['balance']
    #    pass
        #if balance == 0:
        #    raise ValueError('No balance of token at address provided.')
    #except Exception as e:
    #    maybeprint(250, e)

    endpoint = 'token-transfers' if token != '0x0' else 'ether-transfers'
    url = f'https://api.aleth.io/v1/{endpoint}?filter[to]=' + address + '&filter[token]=' + token + '&page%5Blimit%5D=100'
    if token == '0x0':
        url = f'https://api.aleth.io/v1/{endpoint}?filter[account]=' + address + '&page%5Blimit%5D=100'
    if from_address:
        url += '&filter[from]=' + from_address

    # OLD: THIS REQUEST THROWS WITH A 500 INTERNAL SERVER ERROR
    transfers = requests.get(
        url,
        headers=headers
    ).json()

    # NEW: PARSE EVENT LOGS TO SEE WHAT'S GOING ON

    if transfers.get('message') == 'API rate limit exceeded. Please upgrade your account.':
        raise Exception("RATE LIMIT EXCEEDED")
    # TODO - pull more than one page in case there are many transfers.

    if return_what == 'transfers':
        for transfer in transfers.get('data', {}):
            this_is_the_one = tx_id and tx_id.lower() in str(transfer).lower()
            _decimals = transfer.get('attributes', {}).get('decimals', 18)
            _symbol = transfer.get('attributes', {}).get('symbol', 'ETH')
            _value = transfer.get('attributes', {}).get('value', 0)
            _value_decimal = Decimal(int(_value) / 10 ** _decimals)
            _this_is_the_one = False
            for amount in amounts:
                delta = abs(float(abs(_value_decimal)) - float(abs(amount)))
                threshold = (float(abs(amount)) * validation_threshold_pct)
                if delta < threshold or delta < validation_threshold_total:
                    _this_is_the_one = True
            this_is_the_one = not len(amounts) or _this_is_the_one
            if this_is_the_one:
                if transfer.get('type') in ['TokenTransfer', 'EtherTransfer']:
                    return {
                            'token_amount_decimal': _value_decimal,
                            'token_name': _symbol,
                            'to': address,
                            'token_address': token,
                            'token_amount_int': int(transfer['attributes']['value']),
                            'decimals': _decimals,
                    }
        return None

    # TokenTransfer events, value field
    try:
        originators = []
        xfrs = transfers.get('data', {})
        for tx in xfrs:
            if tx.get('type') == 'TokenTransfer':
                response = tx['relationships']['from']['data']['id']
                # hack to save time
                if response != to_address:
                    return [response]
                #originators.append(response)
            value = int(tx.get('attributes', {}).get('value', 0))
            if tx.get('type') == 'EtherTransfer' and value > 0 and token == '0x0':
                response = tx['relationships']['from']['data']['id']
                if response != to_address:
                    # hack to save time
                    return [response]
                    originators.append(response)

        return list(set(originators))
    except Exception as e:
        maybeprint('284', e)
        return []
