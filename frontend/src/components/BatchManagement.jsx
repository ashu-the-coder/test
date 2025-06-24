import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { useTheme } from '../contexts/ThemeContext';
import { ethers } from 'ethers';

function BatchManagement() {
  const { token, userRole } = useContext(AuthContext);
  const { darkMode } = useTheme();
  const navigate = useNavigate();
  
  const [products, setProducts] = useState([]);
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [auditLogs, setAuditLogs] = useState([]);
  const [showAuditModal, setShowAuditModal] = useState(false);
  const [selectedBatchId, setSelectedBatchId] = useState(null);
  const [showContractModal, setShowContractModal] = useState(false);
  const [contractDeploying, setContractDeploying] = useState(false);
  const [contractAddress, setContractAddress] = useState('');
  const [contractError, setContractError] = useState('');
  
  const [showBatchForm, setShowBatchForm] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState('');
  
  const [batchForm, setBatchForm] = useState({
    product_id: '',
    production_date: '',
    expiry_date: '',
    initial_quantity: '',
    batch_number: '',
    batch_notes: '',
    ipfs_cid: '',
    blockchain_tx_hash: ''
  });

  // Validation function for IPFS CID
  const isValidIpfsCid = (cid) => {
    if (!cid) return false;
    // Basic validation for CIDv0 (Qm...) or CIDv1 (bafy...)
    return cid.startsWith('Qm') || cid.startsWith('bafy');
  };
  
  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    
    // Check role-based permissions
    if (!['admin', 'supply_chain_head'].includes(userRole)) {
      setError('You do not have permission to access this module. Required role: admin or supply_chain_head');
    }
    
    fetchProducts();
    fetchBatches();
  }, [token, navigate, userRole]);
  
  const fetchProducts = async () => {
    try {
      const enterpriseId = localStorage.getItem('enterpriseId');
      if (!enterpriseId) {
        throw new Error('Enterprise ID not found');
      }
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/product/list/${enterpriseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch products');
      }
      
      const data = await response.json();
      setProducts(data);
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Failed to load products');
      
      // Mock data for demonstration
      setProducts([
        { id: 'prod_12345', product_name: 'Premium Widget', product_type: 'Hardware', unit: 'piece' },
        { id: 'prod_23456', product_name: 'Standard Gadget', product_type: 'Hardware', unit: 'piece' },
        { id: 'prod_34567', product_name: 'Organic Compound', product_type: 'Chemical', unit: 'liter' }
      ]);
    }
  };
  
  const fetchAuditLogs = async (batchId) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/audit/entity/batch/${batchId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch audit logs');
      }
      
      const data = await response.json();
      setAuditLogs(data);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
      setAuditLogs([]);
    }
  };

  const fetchBatches = async () => {
    setLoading(true);
    try {
      const enterpriseId = localStorage.getItem('enterpriseId');
      if (!enterpriseId) {
        throw new Error('Enterprise ID not found');
      }
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/batch/list/${enterpriseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch batches');
      }
      
      const data = await response.json();
      setBatches(data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching batches:', err);
      
      // Mock data for demonstration
      const mockBatches = [
        { 
          id: 'batch_12345', 
          batch_number: 'PROD001-B001', 
          product_id: 'prod_12345', 
          production_date: '2025-06-01T10:30:00', 
          expiry_date: '2027-06-01T10:30:00', 
          initial_quantity: 1000,
          current_quantity: 950,
          status: 'in_storage',
          qr_code_url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIQAAACEAQAAAABnOuOIAAAA'
        },
        { 
          id: 'batch_23456', 
          batch_number: 'PROD002-B001', 
          product_id: 'prod_23456', 
          production_date: '2025-05-15T09:45:00', 
          expiry_date: '2026-05-15T09:45:00', 
          initial_quantity: 500,
          current_quantity: 500,
          status: 'produced',
          qr_code_url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIQAAACEAQAAAABnOuOIAAAA'
        }
      ];
      setBatches(mockBatches);
      setError('Failed to load batches from server. Displaying mock data.');
      setLoading(false);
    }
  };
  
  const handleBatchFormChange = (e) => {
    const { name, value } = e.target;
    setBatchForm({
      ...batchForm,
      [name]: name === 'initial_quantity' ? parseFloat(value) || '' : value
    });
  };
  
  const handleProductChange = (e) => {
    const productId = e.target.value;
    setSelectedProduct(productId);
    setBatchForm({
      ...batchForm,
      product_id: productId
    });
  };
  
  const handleBatchSubmit = async (e) => {
    e.preventDefault();
    
    // Validate IPFS CID
    if (!isValidIpfsCid(batchForm.ipfs_cid)) {
      setFormError('Invalid IPFS CID. Must start with Qm or bafy.');
      return;
    }
    
    setFormError('');
    
    try {
      // Submit batch to the API
      const response = await fetch(`${import.meta.env.VITE_API_URL}/batch/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(batchForm)
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create batch');
      }
      
      // Show success message with IPFS and blockchain details
      setError('');
      const successMessage = `Batch ${data.batch_number} created successfully! IPFS CID: ${data.ipfs_cid}, Blockchain TX: ${data.blockchain_tx_hash.substring(0, 10)}...`;
      
      // Open QR code modal if available
      if (data.qr_code_url) {
        viewQRCode(data.qr_code_url, data.batch_id);
      }
      
      // Reset form
      setBatchForm({
        product_id: '',
        production_date: '',
        expiry_date: '',
        initial_quantity: '',
        batch_number: '',
        batch_notes: '',
        ipfs_cid: '',
        blockchain_tx_hash: ''
      });
      setSelectedProduct('');
      setShowBatchForm(false);
      
      // Refresh batches list
      fetchBatches();
      
    } catch (err) {
      console.error('Error creating batch:', err);
      setError(err.message || 'Failed to create batch');
    }
  };
  
  const getStatusBadgeColor = (status) => {
    switch(status) {
      case 'produced':
        return darkMode ? 'bg-yellow-700 text-yellow-100' : 'bg-yellow-100 text-yellow-800';
      case 'in_storage':
        return darkMode ? 'bg-blue-700 text-blue-100' : 'bg-blue-100 text-blue-800';
      case 'shipped':
        return darkMode ? 'bg-green-700 text-green-100' : 'bg-green-100 text-green-800';
      case 'received':
        return darkMode ? 'bg-purple-700 text-purple-100' : 'bg-purple-100 text-purple-800';
      case 'sold':
        return darkMode ? 'bg-indigo-700 text-indigo-100' : 'bg-indigo-100 text-indigo-800';
      default:
        return darkMode ? 'bg-gray-700 text-gray-100' : 'bg-gray-100 text-gray-800';
    }
  };
  
  const showAuditTrail = (batchId) => {
    setSelectedBatchId(batchId);
    fetchAuditLogs(batchId);
    setShowAuditModal(true);
  };
  
  const closeAuditModal = () => {
    setShowAuditModal(false);
    setSelectedBatchId(null);
    setAuditLogs([]);
  };
  
  const deploySmartContract = async () => {
    if (!window.ethereum) {
      setContractError('MetaMask or similar wallet not detected. Please install MetaMask to deploy contracts.');
      return;
    }
    
    try {
      setContractDeploying(true);
      setContractError('');
      
      // Connect to the wallet
      await window.ethereum.request({ method: 'eth_requestAccounts' });
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      
      // XineteStorage Contract ABI and Bytecode
      const contractABI = [
        "function storeCID(string memory cid, string memory hash) public",
        "function getCIDs(address user) public view returns (string[] memory)",
        "function verifyOwnership(address user, string memory cid) public view returns (bool)",
        "function getCIDByHash(string memory hash) public view returns (string memory)",
        "function removeCID(address user, string memory cid) public",
        "event CIDStored(address indexed user, string cid, string hash)",
        "event CIDRemoved(address indexed user, string cid)"
      ];
      
      const contractBytecode = "0x608060405234801561001057600080fd5b50610acd806100206000396000f3fe608060405234801561001057600080fd5b50600436106100575760003560e01c80630b977dc41461005c57806318668ba31461008c57806338e2860d146100bc578063c0d275f0146100ec578063e4397333146101385761005b565b5b005b61007660048036038101906100719190610638565b61016b565b60405161008391906106be565b60405180910390f35b6100a660048036038101906100a191906106f9565b610254565b6040516100b39190610803565b60405180910390f35b6100d660048036038101906100d1919061081e565b6102bc565b6040516100e39190610803565b60405180910390f35b6101226004803603810190610121919061086e565b61033c565b60405161012f91906106be565b60405180910390f35b610152600480360381019061014d91906108c7565b61045a565b60405161016294939291906109a0565b60405180910390f35b60606000808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002080548060200260200160405190810160405280929190818152602001828054801561024857602002820191906000526020600020905b8154815260200190600101908083116102345750505050509050919050565b60008061026083610611565b9050600061027d82858960405160200161027c93929190610a3d565b5b60405160208183030381529060405261052e565b9050807f9cc3a881ffcc92154953391c294f00d84e42ac04590ab13fd09cc5485580b07a8686866040516102b393929190610a72565b60405180910390a2809450505050505b92915050565b60008060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002080549050905060008167ffffffffffffffff81111561031757610316610913565b5b6040519080825280602002602001820160405280156103455781602001602082028036833780820191505090505b509150600090505b818110156103325760008060008873ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000208281548110610397576103966108e4565b5b9060005260206000200154905080848381518110610366576103656108e4565b5b60200260200101818152505080806103279061094a565b91505061034d565b8192505050949350505050565b6000806000848152602001908152602001600020546000141561036057600080fd5b600080600084815260200190815260200160002060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff169050600084846040516020016103a892919061091c565b604051602081830303815290604052805190602001206040516020016103d092919061091c565b604051602081830303815290604052805190602001208214156104525760008060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002083815481106104425761044161094a565b5b90600052602060002001546000808581526020019081526020016000208190555060019150505b92915050565b600080600080600080868152602001908152602001600020546000141561054a576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004016104d3906109d1565b60405180910390fd5b50505b9193509193509193565b6000807f9f2df0fed2c77648de5860a4cc508cd0818c85b8b8a1ab4ceeef8d981c8956a6905060006040518060200161052d91906109f1565b60405160208183030381529060405280519060200120905061059e8184866040516020016105999392919061091c565b5b6040516020818303038152906040528051906020012083610600565b9250505092915050565b600080836040516020016105b9919061091c565b604051602081830303815290604052805190602001209050600080848152602001908152602001600020549150509392505050565b60008160405160200161060c919061091c565b604051602081830303815290604052805190602001209050919050565b600081359050610632816109e4565b92915050565b60006020828403121561064c57600080fd5b600061065a84828501610623565b91505092915050565b600061066e826109d1565b61067881856109e0565b9350610688818560208601610a0c565b61069181610a3f565b840191505092915050565b60006106a7826109d1565b6106b181856109e0565b93506106c1818560208601610a0c565b80840191505092915050565b600060208201905081810360008301526106e68184610663565b905092915050565b60008135905061069181610a50565b600080600060608486031215610710576106a7600080fd5b600061071e86828701610623565b935050602061072f86828701610623565b925050604061074086828701610623565b9150509250925092565b60008151905061075981610a77565b92915050565b60008151905061076e81610a8e565b92915050565b60008151905061078381610aa5565b92915050565b60008151905061079881610abc565b92915050565b600081519050600081815260208301602085015260408301602085015260608301602085015260808301602085015260a08301602085015260c08301602085015260e08301602085015261010083016020850152610120830160208501526101408301602085015261016083016020850152610180830160208501526101a083016020850152509392505050565b6000602082019050818103600083015261083881846106a7565b905092915050565b60008060008060008061010087890312156103ba576103157600080fd5b60008061083e8c828d01610623565b975050602061084f8c828d01610623565b96505060408b013567ffffffffffffffff81111561086c57600080fd5b6108788d828e01610773565b955050606061088a8d828e01610773565b945050608061089c8d828e01610774565b93505060a06108ae8d828e01610774565b92505060c06108c08d828e01610789565b91505092959891949750929550565b600080604083850312156108da576108d9600080fd5b60006108e885828601610623565b92505060206108f98582860161074a565b9150509250929050565b6000806040838503121561091b57600080fd5b6000610366858286016107a9565b82818337600083830152505050565b600060208201905061095a6000830184610774565b92915050565b6000602082019050610975600083018461075f565b92915050565b600060208201905061099060008301846107a9565b92915050565b60006080820190506109ab6000830187610774565b6109b86020830186610774565b6109c56040830185610789565b81810360608301526109d7818461069c565b905095945050505050565b600081519050919050565b600081905092915050565b600073ffffffffffffffffffffffffffffffffffffffff82169050919050565b60005b83811015610a25578082015181840152602081019050610a0a565b83811115610a34576000848401525b50505050565b600060e01b82169050919050565b610a538161099f565b8114610a5e57600080fd5b50565b610a6c816109af565b8114610a7757600080fd5b50565b610a8081610774565b8114610a8b57600080fd5b50565b610a9781610789565b8114610aa257600080fd5b50565b610aae816109cf565b8114610ab957600080fd5b50565b610ac5816109db565b8114610ad057600080fd5b50565b6109e4816109db565b5056fea264697066735822122086dfeffdc885c26a0cca0299748ca4292e8bae9d0ce03914d0a8d664648769ee64736f6c6343000807003300000000000000000000000000000";

      // Deploy the contract
      const factory = new ethers.ContractFactory(contractABI, contractBytecode, signer);
      const contract = await factory.deploy();
      await contract.waitForDeployment();
      
      // Get deployed contract address
      const deployedAddress = await contract.getAddress();
      setContractAddress(deployedAddress);
      
      // Store contract address in localStorage
      localStorage.setItem('xineteStorageContractAddress', deployedAddress);
      
      setContractDeploying(false);
      
      // Notify success
      alert('Smart contract deployed successfully!');
      
    } catch (error) {
      console.error('Error deploying contract:', error);
      setContractError(error.message || 'Failed to deploy smart contract');
      setContractDeploying(false);
    }
  };
  
  const closeContractModal = () => {
    setShowContractModal(false);
    setContractError('');
  };

  const viewQRCode = (qrUrl, batchId) => {
    const batch = batches.find(b => b.id === batchId);
    const verificationUrl = batch?.verification_url || `https://xinete.io/verify/${batchId}`;
    const ipfsCid = batch?.ipfs_cid || '';
    
    // Create a modal dialog to show the QR code and verification URL
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100%';
    modal.style.height = '100%';
    modal.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
    modal.style.display = 'flex';
    modal.style.justifyContent = 'center';
    modal.style.alignItems = 'center';
    modal.style.zIndex = '1000';
    
    const content = document.createElement('div');
    content.style.backgroundColor = darkMode ? '#1a202c' : 'white';
    content.style.padding = '20px';
    content.style.borderRadius = '8px';
    content.style.maxWidth = '400px';
    content.style.color = darkMode ? 'white' : 'black';
    
    // Add QR image
    const img = document.createElement('img');
    img.src = qrUrl;
    img.style.width = '300px';
    img.style.height = '300px';
    img.style.display = 'block';
    img.style.margin = '0 auto 20px';
    
    // Add verification link
    const link = document.createElement('div');
    link.style.textAlign = 'center';
    link.style.marginBottom = '15px';
    link.innerHTML = `<a href="${verificationUrl}" target="_blank" style="color: ${darkMode ? '#90cdf4' : '#3182ce'}; text-decoration: underline;">Verification Link</a>`;
    
    // Add IPFS link if available
    if (ipfsCid) {
      const ipfsLink = document.createElement('div');
      ipfsLink.style.textAlign = 'center';
      ipfsLink.style.marginBottom = '15px';
      ipfsLink.innerHTML = `<a href="https://ipfs.io/ipfs/${ipfsCid}" target="_blank" style="color: ${darkMode ? '#90cdf4' : '#3182ce'}; text-decoration: underline;">View on IPFS</a>`;
      content.appendChild(ipfsLink);
    }
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.innerText = 'Close';
    closeBtn.style.padding = '8px 16px';
    closeBtn.style.backgroundColor = darkMode ? '#4a5568' : '#e2e8f0';
    closeBtn.style.color = darkMode ? 'white' : 'black';
    closeBtn.style.border = 'none';
    closeBtn.style.borderRadius = '4px';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.display = 'block';
    closeBtn.style.margin = '0 auto';
    closeBtn.onclick = () => document.body.removeChild(modal);
    
    // Assemble modal
    content.appendChild(img);
    content.appendChild(link);
    content.appendChild(closeBtn);
    modal.appendChild(content);
    
    // Add click outside to close
    modal.addEventListener('click', (e) => {
      if (e.target === modal) document.body.removeChild(modal);
    });
    
    // Add to document
    document.body.appendChild(modal);
  };
  
  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'} transition-colors duration-200 py-10 px-4 sm:px-6 lg:px-8`}>
      <div className="max-w-7xl mx-auto">
        <div className="mb-10 flex justify-between items-center">
          <h1 className="text-3xl font-bold">Batch Management</h1>
          <button
            onClick={() => navigate('/enterprise/modules')}
            className={`px-4 py-2 rounded-md ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'} transition duration-200`}
          >
            Back to Modules
          </button>
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-red-100 border-l-4 border-red-500 text-red-700 dark:bg-red-900 dark:text-red-300">
            {error}
          </div>
        )}
        
        {/* Role permission warning */}
        {!['admin', 'supply_chain_head'].includes(userRole) && (
          <div className="mb-6 p-4 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300">
            <p className="font-bold">Access Restricted</p>
            <p>You do not have permission to modify batches. Required role: admin or supply_chain_head.</p>
          </div>
        )}
        
        <div className="mb-6 flex justify-end space-x-4">
          <button
            onClick={() => navigate('/enterprise/inventory')}
            className={`px-4 py-2 rounded-md ${darkMode ? 'bg-green-600 hover:bg-green-700' : 'bg-green-500 hover:bg-green-600'} text-white transition duration-200 flex items-center`}
          >
            <span className="mr-2">Manage Inventory</span>
            <span>📊</span>
          </button>
          {/* Only show create batch button for users with proper permissions */}
          {['admin', 'supply_chain_head'].includes(userRole) && (
            <button
              onClick={() => setShowBatchForm(!showBatchForm)}
              className={`px-4 py-2 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200 flex items-center`}
            >
              <span className="mr-2">
                {showBatchForm ? 'Cancel' : 'Create New Batch'}
              </span>
              {!showBatchForm && <span>+</span>}
            </button>
          )}
        </div>
        
        {showBatchForm && (
          <div className={`mb-8 p-6 rounded-md shadow-md ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
            <h2 className="text-xl font-semibold mb-4">Create New Batch</h2>
            <form onSubmit={handleBatchSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                    Product
                  </label>
                  <select
                    value={selectedProduct}
                    onChange={handleProductChange}
                    className={`w-full px-3 py-2 border rounded-md ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                    required
                  >
                    <option value="">Select Product</option>
                    {products.map((product) => (
                      <option key={product.id} value={product.id}>
                        {product.product_name} ({product.unit})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                    Batch Number (Optional)
                  </label>
                  <input
                    type="text"
                    name="batch_number"
                    value={batchForm.batch_number}
                    onChange={handleBatchFormChange}
                    placeholder="Leave blank for auto-generation"
                    className={`w-full px-3 py-2 border rounded-md ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  />
                </div>
                <div>
                  <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                    Production Date
                  </label>
                  <input
                    type="datetime-local"
                    name="production_date"
                    value={batchForm.production_date}
                    onChange={handleBatchFormChange}
                    className={`w-full px-3 py-2 border rounded-md ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                    required
                  />
                </div>
                <div>
                  <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                    Expiry Date
                  </label>
                  <input
                    type="datetime-local"
                    name="expiry_date"
                    value={batchForm.expiry_date}
                    onChange={handleBatchFormChange}
                    className={`w-full px-3 py-2 border rounded-md ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  />
                </div>
                <div>
                  <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                    Initial Quantity
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    name="initial_quantity"
                    value={batchForm.initial_quantity}
                    onChange={handleBatchFormChange}
                    className={`w-full px-3 py-2 border rounded-md ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                    required
                  />
                </div>
                <div className="md:col-span-2">
                  <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                    Batch Notes
                  </label>
                  <textarea
                    name="batch_notes"
                    rows="3"
                    value={batchForm.batch_notes}
                    onChange={handleBatchFormChange}
                    className={`w-full px-3 py-2 border rounded-md ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  ></textarea>
                </div>
                <div>
                  <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                    IPFS CID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    name="ipfs_cid"
                    value={batchForm.ipfs_cid}
                    onChange={handleBatchFormChange}
                    placeholder="IPFS Content ID for batch documentation"
                    className={`w-full px-3 py-2 border rounded-md ${
                      !batchForm.ipfs_cid ? 'border-red-500' : 
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                    required
                  />
                  <p className={`mt-1 text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                    Required - IPFS CID for batch documentation (must start with Qm or bafy)
                  </p>
                </div>
                <div>
                  <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                    Blockchain TX Hash
                  </label>
                  <input
                    type="text"
                    name="blockchain_tx_hash"
                    value={batchForm.blockchain_tx_hash}
                    onChange={handleBatchFormChange}
                    placeholder="Blockchain transaction hash"
                    className={`w-full px-3 py-2 border rounded-md ${
                      darkMode 
                        ? 'bg-gray-700 border-gray-600 text-white' 
                        : 'bg-white border-gray-300 text-gray-900'
                    } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  />
                  <p className={`mt-1 text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                    Leave blank - a blockchain transaction will be automatically generated (required field)
                  </p>
                </div>
              </div>
              {formError && (
                <div className="mt-4 p-3 bg-red-100 border-l-4 border-red-500 text-red-700 rounded-md">
                  {formError}
                </div>
              )}
              {formError && (
                <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                  <p>{formError}</p>
                </div>
              )}
              <div className="mt-6">
                <button
                  type="submit"
                  className={`px-5 py-2 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200`}
                >
                  Create Batch
                </button>
              </div>
            </form>
          </div>
        )}
        
        {/* Batches Table */}
        <div className={`overflow-x-auto rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} shadow-md`}>
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className={`${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Batch Number
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Product
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Production Date
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Quantity
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-center text-xs font-medium uppercase tracking-wider">
                  QR Code
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {batches.length > 0 ? (
                batches.map((batch) => (
                  <tr key={batch.id} className={`${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'}`}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {batch.batch_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {products.find(p => p.id === batch.product_id)?.product_name || 'Unknown Product'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {new Date(batch.production_date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {batch.current_quantity} {products.find(p => p.id === batch.product_id)?.unit || 'units'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeColor(batch.status)}`}>
                        {batch.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      {batch.qr_code_url ? (
                        <button
                          onClick={() => viewQRCode(batch.qr_code_url, batch.id)}
                          className={`inline-flex items-center justify-center ${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-800'}`}
                        >
                          <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                            <path d="M2 4a2 2 0 012-2h4a1 1 0 010 2H4v4a1 1 0 01-2 0V4zm10-2a1 1 0 011 1v1h1a1 1 0 110 2h-1v1a1 1 0 11-2 0V6h-1a1 1 0 110-2h1V3a1 1 0 011-1zm4 8a1 1 0 01.993.883L17 11v5a2 2 0 01-2 2H9a1 1 0 110-2h6v-5a1 1 0 011-1zM2 14a1 1 0 011 1v1h5a1 1 0 110 2H3a2 2 0 01-2-2v-1a1 1 0 011-1z" />
                          </svg>
                          <span className="ml-1">QR Code</span>
                        </button>
                      ) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button 
                        onClick={() => navigate(`/enterprise/traceability?batch=${batch.id}`)}
                        className={`${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-900'} mr-3`}
                      >
                        Events
                      </button>
                      <button 
                        onClick={() => showAuditTrail(batch.id)}
                        className={`${darkMode ? 'text-green-400 hover:text-green-300' : 'text-green-600 hover:text-green-900'}`}
                      >
                        Audit Log
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="px-6 py-4 text-center">
                    No batches found. Create your first batch.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        
        {/* Audit Log Modal */}
        {showAuditModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className={`${darkMode ? 'bg-gray-800' : 'bg-white'} rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden`}>
              <div className="p-5 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <h3 className="text-xl font-semibold">
                  Audit Trail for Batch {batches.find(b => b.id === selectedBatchId)?.batch_number || selectedBatchId}
                </h3>
                <button 
                  onClick={closeAuditModal}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <svg className="h-6 w-6" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                </button>
              </div>
              
              <div className="p-5 overflow-y-auto max-h-[60vh]">
                {auditLogs.length > 0 ? (
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className={`${darkMode ? 'bg-gray-700' : 'bg-gray-50'} sticky top-0`}>
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider">Date/Time</th>
                        <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider">Field Changed</th>
                        <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider">Old Value</th>
                        <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider">New Value</th>
                        <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider">Changed By</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                      {auditLogs.map((log, index) => (
                        <tr key={index} className={index % 2 === 0 ? 'bg-gray-50 dark:bg-gray-700' : ''}>
                          <td className="px-3 py-2 whitespace-nowrap text-sm">{new Date(log.timestamp).toLocaleString()}</td>
                          <td className="px-3 py-2 whitespace-nowrap text-sm">{log.field_changed}</td>
                          <td className="px-3 py-2 text-sm">{typeof log.old_value === 'object' ? JSON.stringify(log.old_value) : String(log.old_value)}</td>
                          <td className="px-3 py-2 text-sm">{typeof log.new_value === 'object' ? JSON.stringify(log.new_value) : String(log.new_value)}</td>
                          <td className="px-3 py-2 whitespace-nowrap text-sm">{log.changed_by}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="text-center py-10">
                    <p className="text-gray-500 dark:text-gray-400">No audit logs found for this batch.</p>
                  </div>
                )}
              </div>
              
              <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
                <button
                  onClick={closeAuditModal}
                  className={`px-4 py-2 rounded-md ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'} transition duration-200`}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default BatchManagement;
