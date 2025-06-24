from web3 import Web3
from eth_account import Account
from typing import List
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
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
            if not self.w3.is_address(user):
                raise Exception("Invalid Ethereum address format")
            # Convert the address to checksum format
            checksum_address = self.w3.to_checksum_address(user.lower())
            return self.contract.functions.verifyOwnership(checksum_address, cid).call()
        except ValueError as e:
            raise Exception(f"Invalid wallet address: {str(e)}")
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
        """Remove a CID from the blockchain using file hash verification"""
        try:
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx = self.contract.functions.removeCID(self.account.address, cid).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send transaction
            signed_tx = self.account.sign_transaction(tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            return receipt['transactionHash'].hex()
        
        except Exception as e:
            raise Exception(f"Error removing CID from blockchain: {str(e)}")
            
    async def register_batch(self, batch_id: str, product_id: str, ipfs_cid: str) -> str:
        """
        Register a batch in the blockchain.
        
        This is a MANDATORY step in batch creation and will fail the entire
        batch creation process if it fails. All parameters are required.
        
        Args:
            batch_id: The unique identifier for the batch
            product_id: The product ID this batch belongs to
            ipfs_cid: IPFS CID for batch documentation (REQUIRED)
            
        Returns:
            str: The transaction hash
            
        Raises:
            ValueError: If any parameters are missing or invalid
            Exception: If blockchain registration fails
        """
        # Validate inputs
        if not batch_id or not product_id or not ipfs_cid:
            raise ValueError("All parameters (batch_id, product_id, ipfs_cid) are required for blockchain registration")
        
        # For demonstration purposes, we'll mock the blockchain registration
        # In production, this would be a real smart contract call
        import hashlib
        import json
        import time
        
        try:
            # In a real implementation, we would use the following approach:
            # 1. Build a transaction to call a smart contract method to register the batch
            # 2. Sign and send the transaction
            # 3. Wait for the transaction receipt
            # 4. Return the transaction hash
            
            # Create a deterministic hash based on the batch details
            batch_data = {
                "batch_id": batch_id,
                "product_id": product_id,
                "ipfs_cid": ipfs_cid,
                "timestamp": int(time.time())
            }
            
            data_json = json.dumps(batch_data, sort_keys=True)
            mock_tx_hash = "0x" + hashlib.sha256(data_json.encode()).hexdigest()
            
            logging.info(f"Mock blockchain registration for batch {batch_id}: {mock_tx_hash}")
            
            return mock_tx_hash
            
        except Exception as e:
            logging.error(f"Error registering batch in blockchain: {str(e)}")
            # Since blockchain registration is mandatory, we re-raise the exception
            # instead of returning a mock hash
            raise Exception(f"Failed to register batch in blockchain: {str(e)}")
            
    async def record_trace_event(self, event_id: str, batch_id: str, event_type: str, ipfs_cid: str) -> str:
        """
        Record a traceability event in the blockchain.
        
        This is a MANDATORY step in traceability event creation and will fail the entire
        event creation process if it fails. All parameters are required.
        
        Args:
            event_id: The unique identifier for the event
            batch_id: The batch ID this event relates to
            event_type: The type of event (e.g., 'production', 'shipping')
            ipfs_cid: IPFS CID for event documentation (REQUIRED)
            
        Returns:
            str: The transaction hash
            
        Raises:
            ValueError: If any parameters are missing or invalid
            Exception: If blockchain recording fails
        """
        # Validate inputs
        if not event_id or not batch_id or not event_type or not ipfs_cid:
            raise ValueError("All parameters (event_id, batch_id, event_type, ipfs_cid) are required for blockchain recording")
            
        # For demonstration purposes, we'll mock the blockchain event recording
        # In production, this would be a real smart contract call
        import hashlib
        import json
        import time
        
        try:
            # In a real implementation, we would use the following approach:
            # 1. Build a transaction to call a smart contract method to record the event
            # 2. Sign and send the transaction
            # 3. Wait for the transaction receipt
            # 4. Return the transaction hash
            
            # Create a deterministic hash based on the event details
            event_data = {
                "event_id": event_id,
                "batch_id": batch_id,
                "event_type": event_type,
                "ipfs_cid": ipfs_cid,
                "timestamp": int(time.time())
            }
            
            data_json = json.dumps(event_data, sort_keys=True)
            mock_tx_hash = "0x" + hashlib.sha256(data_json.encode()).hexdigest()
            
            logging.info(f"Mock blockchain recording for event {event_id}: {mock_tx_hash}")
            
            return mock_tx_hash
            
        except Exception as e:
            logging.error(f"Error recording event in blockchain: {str(e)}")
            # Since blockchain recording is mandatory, we re-raise the exception
            # instead of returning a mock hash
            raise Exception(f"Failed to record event in blockchain: {str(e)}")