from web3 import Web3
from eth_account import Account
from typing import List
import os
from dotenv import load_dotenv

class BlockchainService:
    def __init__(self):
        load_dotenv()
        
        # Connect to SKALE network
        self.w3 = Web3(Web3.HTTPProvider(os.getenv("SKALE_ENDPOINT")))
        
        # Load contract details
        self.contract_address = os.getenv("CONTRACT_ADDRESS")
        self.contract_abi = [
            {
                "inputs": [{"internalType": "string", "name": "cid", "type": "string"}],
                "name": "storeCID",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
                "name": "getCIDs",
                "outputs": [{"internalType": "string[]", "name": "", "type": "string[]"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "user", "type": "address"},
                    {"internalType": "string", "name": "cid", "type": "string"}
                ],
                "name": "verifyOwnership",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "address", "name": "user", "type": "address"},
                    {"internalType": "string", "name": "cid", "type": "string"}
                ],
                "name": "removeCID",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        # Initialize contract
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        
        # Load account
        private_key = os.getenv("PRIVATE_KEY")
        self.account = Account.from_key(private_key)
    
    async def store_cid(self, user: str, cid: str) -> str:
        """Store a CID in the blockchain"""
        try:
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx = self.contract.functions.storeCID(cid).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt['transactionHash'].hex()
        
        except Exception as e:
            raise Exception(f"Error storing CID in blockchain: {str(e)}")
    
    async def get_user_cids(self, user: str) -> List[str]:
        """Get all CIDs for a user from the blockchain"""
        try:
            return self.contract.functions.getCIDs(user).call()
        except Exception as e:
            raise Exception(f"Error getting CIDs from blockchain: {str(e)}")
    
    async def verify_ownership(self, user: str, cid: str) -> bool:
        """Verify if a user owns a specific CID"""
        try:
            return self.contract.functions.verifyOwnership(user, cid).call()
        except Exception as e:
            raise Exception(f"Error verifying ownership: {str(e)}")
    
    async def remove_cid(self, user: str, cid: str) -> str:
        """Remove a CID from the blockchain"""
        try:
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx = self.contract.functions.removeCID(user, cid).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt['transactionHash'].hex()
        
        except Exception as e:
            raise Exception(f"Error removing CID from blockchain: {str(e)}")