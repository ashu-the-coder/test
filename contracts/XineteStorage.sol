// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract XineteStorage {
    // Mapping from user address to their CIDs
    mapping(address => string[]) private userCIDs;
    
    // Mapping to track CID ownership
    mapping(string => address) private cidOwnership;
    
    // Mapping to store hash to CID relationship
    mapping(string => string) private hashToCID;
    
    // Event emitted when a new CID is stored
    event CIDStored(address indexed user, string cid, string hash);
    
    // Event emitted when a CID is removed
    event CIDRemoved(address indexed user, string cid);
    
    /**
     * @dev Store a CID for the sender
     * @param cid The IPFS CID to store
     */
    function storeCID(string memory cid, string memory hash) public {
        require(bytes(cid).length > 0, "CID cannot be empty");
        require(bytes(hash).length > 0, "Hash cannot be empty");
        require(cidOwnership[cid] == address(0), "CID already exists");
        require(bytes(hashToCID[hash]).length == 0, "Hash already exists");
        
        userCIDs[msg.sender].push(cid);
        cidOwnership[cid] = msg.sender;
        hashToCID[hash] = cid;
        
        emit CIDStored(msg.sender, cid, hash);
    }
    
    /**
     * @dev Get all CIDs for a specific user
     * @param user The address of the user
     * @return An array of CIDs belonging to the user
     */
    function getCIDs(address user) public view returns (string[] memory) {
        return userCIDs[user];
    }
    
    /**
     * @dev Verify if a user owns a specific CID
     * @param user The address of the user
     * @param cid The CID to verify
     * @return bool indicating ownership
     */
    function verifyOwnership(address user, string memory cid) public view returns (bool) {
        return cidOwnership[cid] == user;
    }
    
    /**
     * @dev Get CID by hash
     * @param hash The hash to lookup
     * @return The corresponding CID
     */
    function getCIDByHash(string memory hash) public view returns (string memory) {
        string memory cid = hashToCID[hash];
        require(bytes(cid).length > 0, "Hash not found");
        return cid;
    }
    
    /**
     * @dev Remove a CID from a user's storage
     * @param user The address of the user
     * @param cid The CID to remove
     */
    function removeCID(address user, string memory cid) public {
        require(msg.sender == user, "Only the owner can remove their CIDs");
        require(cidOwnership[cid] == user, "CID does not belong to user");
        
        // Remove CID from userCIDs array
        uint256 length = userCIDs[user].length;
        for (uint256 i = 0; i < length; i++) {
            if (keccak256(bytes(userCIDs[user][i])) == keccak256(bytes(cid))) {
                // Move the last element to the position of the element to delete
                userCIDs[user][i] = userCIDs[user][length - 1];
                // Remove the last element
                userCIDs[user].pop();
                break;
            }
        }
        
        // Remove CID ownership
        delete cidOwnership[cid];
        
        emit CIDRemoved(user, cid);
    }
}