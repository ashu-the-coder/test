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
                "inputs": [
                    {"internalType": "string", "name": "cid", "type": "string"},
                    {"internalType": "string", "name": "hash", "type": "string"}
                ],
                "name": "storeCID",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "string", "name": "hash", "type": "string"}],
                "name": "getCIDByHash",
                "outputs": [{"internalType": "string", "name": "", "type": "string"}],
                "stateMutability": "view",
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
    
    async def store_cid(self, user: str, cid: str, file_hash: str) -> str:
        """Store a CID with its hash in the blockchain"""
        try:
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx = self.contract.functions.storeCID(cid, file_hash).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, os.getenv("PRIVATE_KEY"))
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
    
    async def get_cid_by_hash(self, file_hash: str) -> str:
        """Get CID by its hash from the blockchain"""
        try:
            cid = self.contract.functions.getCIDByHash(file_hash).call()
            if not cid:
                logging.error(f"CID not found in blockchain for hash '{file_hash}'")
                raise Exception("File exists in metadata but not found in blockchain. The file may have been removed from the blockchain.")
            logging.info(f"Successfully retrieved CID '{cid}' from blockchain for hash '{file_hash}'")
            return cid
        except Exception as e:
            if "Hash not found" in str(e) or "revert" in str(e).lower():
                logging.error(f"CID not found in blockchain for hash '{file_hash}'")
                raise Exception("File exists in metadata but not found in blockchain. The file may have been removed from the blockchain.")
            raise Exception(f"Error getting CID by hash: {str(e)}")
    
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
            signed_tx = self.w3.eth.account.sign_transaction(tx, os.getenv("PRIVATE_KEY"))
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt['transactionHash'].hex()
        
        except Exception as e:
            raise Exception(f"Error removing CID from blockchain: {str(e)}")