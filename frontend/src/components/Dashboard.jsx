import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../App';
import { ethers } from 'ethers';
import FileUpload from './FileUpload';
import { FiDownload } from 'react-icons/fi';

function Dashboard() {
  const [files, setFiles] = useState([]);
  const [error, setError] = useState('');
  const { token, isConnected } = useContext(AuthContext);

  useEffect(() => {
    if (token) {
      fetchFiles();
    }
  }, [token]);

  const handleDownload = async (file) => {
    if (!token) {
      setError('Authentication token is missing');
      return;
    }

    try {
      console.log(`Attempting to download file with hash: ${file.hash}`);
      
      const response = await fetch(`http://localhost:8000/storage/download/${file.hash}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error('Download failed:', errorData);
        if (response.status === 404) {
          throw new Error('File not found in blockchain. The file may have been deleted.');
        } else if (response.status === 403) {
          throw new Error('You are not authorized to download this file.');
        } else {
          throw new Error(errorData.detail || 'Failed to download file');
        }
      }
      
      console.log('Successfully retrieved file from blockchain and IPFS');

      const contentDisposition = response.headers.get('content-disposition');
      const filename = contentDisposition
        ? contentDisposition.split('filename=')[1]
        : file.filename;

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
      const response = await fetch('http://localhost:8000/storage/files', {
        headers: {
          'Authorization': `Bearer ${token}`,
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
          {files.map((file, index) => (
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
                <button
                  onClick={() => handleDownload(file)}
                  className="flex items-center gap-2 px-3 py-1 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  <FiDownload className="w-4 h-4" />
                  Download
                </button>
              </div>
            </div>
          ))}
          {files.length === 0 && (
            <p className="text-gray-500 dark:text-gray-400 text-center py-4">
              No files uploaded yet
            </p>
          )}
        </div>
      </div>
    </div>
    </div>
  );
}

export default Dashboard;