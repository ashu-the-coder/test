import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../App';
import { ethers } from 'ethers';
import FileUpload from './FileUpload';
import { FiDownload, FiTrash2 } from 'react-icons/fi';

function Dashboard() {
  const [files, setFiles] = useState([]);
  const [error, setError] = useState('');
  const { token, isConnected, userAddress } = useContext(AuthContext);

  const connectWallet = async () => {
    try {
      if (!window.ethereum) {
        throw new Error('Please install MetaMask to use this application');
      }

      await window.ethereum.request({ method: 'eth_requestAccounts' });
      const provider = new ethers.BrowserProvider(window.ethereum);
      await provider.getSigner();
      return true;
    } catch (err) {
      setError('Failed to connect wallet: ' + err.message);
      return false;
    }
  };

  useEffect(() => {
    if (token) {
      fetchFiles();
    }
  }, [token]);

  const handleDelete = async (file) => {
    if (!token) {
      setError('Authentication token is missing');
      return;
    }

    if (!isConnected || !userAddress) {
      const connected = await connectWallet();
      if (!connected) {
        setError('Please connect your wallet to delete files');
        return;
      }
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/storage/delete/${file.file_hash}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Wallet-Address': userAddress
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete file');
      }

      // Update the files list after successful deletion
      setFiles(files.filter(f => f.file_hash !== file.file_hash));
      setError('');
    } catch (err) {
      setError('Error deleting file: ' + err.message);
    }
  };

  const handleDownload = async (file) => {
    if (!token) {
      setError('Authentication token is missing');
      return;
    }

    if (!isConnected || !userAddress) {
      const connected = await connectWallet();
      if (!connected) {
        setError('Please connect your wallet to download files');
        return;
      }
    }

    try {
      console.log(`Attempting to download file with hash: ${file.file_hash}`);
      
      // First get the IPFS URL and CID from the backend
      const cidResponse = await fetch(`${import.meta.env.VITE_API_URL}/storage/download/${file.file_hash}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Wallet-Address': userAddress
        },
      });

      if (!cidResponse.ok) {
        const errorData = await cidResponse.json();
        console.error('Download failed:', errorData);
        if (cidResponse.status === 404) {
          throw new Error('File not found in blockchain. The file may have been deleted.');
        } else if (cidResponse.status === 403) {
          throw new Error('You are not authorized to download this file.');
        } else {
          throw new Error(errorData.detail || 'Failed to download file');
        }
      }

      const { ipfs_url } = await cidResponse.json();
      // Download file from self-hosted IPFS gateway
      const response = await fetch(ipfs_url);
      if (!response.ok) {
        throw new Error('Failed to download file from IPFS');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');

      a.href = url;
      a.download = file.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Error downloading file: ' + err.message);
    }
  };

  const fetchFiles = async () => {
    if (!token) {
      setError('Authentication token is missing');
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/storage/files`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'X-Wallet-Address': userAddress
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch files');
      }

      const data = await response.json();
      setFiles(data.files);
      setError('');
    } catch (err) {
      setError('Error fetching files: ' + err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="space-y-6">
      <FileUpload onUploadSuccess={fetchFiles} />
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Your Files</h2>
        {error && (
          <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
          </div>
        )}
        <div className="space-y-4">
          {(Array.isArray(files) ? files : []).map((file, index) => (
            <div key={index} className="p-4 border dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <p className="font-medium text-gray-900 dark:text-white">{file.filename}</p>
              <div className="flex items-center justify-between mt-2">
                <div>
                  <p className="text-gray-600 dark:text-gray-400 text-sm">
                    Uploaded: {new Date(file.upload_date).toLocaleDateString()}
                  </p>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    Size: {(file.size / 1024).toFixed(2)} KB
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleDownload(file)}
                    className="flex items-center gap-2 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                  >
                    <FiDownload className="w-4 h-4" />
                    Download
                  </button>
                  <button
                    onClick={() => handleDelete(file)}
                    className="flex items-center gap-2 px-3 py-1 text-sm text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                  >
                    <FiTrash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      </div>
    </div>
  );
}

export default Dashboard;