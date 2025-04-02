import { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../App';
import { ethers } from 'ethers';

function Dashboard() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const { token, isConnected } = useContext(AuthContext);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const response = await fetch('http://localhost:8000/storage/files', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch files');

      const data = await response.json();
      setFiles(data.files);
    } catch (err) {
      setError('Error fetching files: ' + err.message);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/storage/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const data = await response.json();
      await fetchFiles(); // Refresh file list
    } catch (err) {
      setError('Error uploading file: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDownload = async (cid) => {
    try {
      const response = await fetch(`http://localhost:8000/storage/file/${cid}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Download failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `file-${cid}`; // You might want to store original filenames in metadata
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Error downloading file: ' + err.message);
    }
  };

  const handleDelete = async (cid) => {
    try {
      const response = await fetch(`http://localhost:8000/storage/file/${cid}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Delete failed');

      await fetchFiles(); // Refresh file list
    } catch (err) {
      setError('Error deleting file: ' + err.message);
    }
  };

  if (!isConnected) {
    return (
      <div className="text-center py-8">
        <p className="text-red-500">Please connect your wallet to continue</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload File
        </label>
        <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
          <div className="space-y-1 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div className="flex text-sm text-gray-600">
              <label
                htmlFor="file-upload"
                className="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
              >
                <span>Upload a file</span>
                <input
                  id="file-upload"
                  name="file-upload"
                  type="file"
                  className="sr-only"
                  onChange={handleFileUpload}
                  disabled={uploading}
                />
              </label>
            </div>
            <p className="text-xs text-gray-500">Any file up to 10MB</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
          {error}
        </div>
      )}

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {files.map((file) => (
            <li key={file.cid}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-indigo-600 truncate">
                    {file.cid}
                  </p>
                  <div className="ml-2 flex-shrink-0 flex">
                    <button
                      onClick={() => handleDownload(file.cid)}
                      className="mr-2 px-2 py-1 text-xs font-medium text-green-700 bg-green-100 rounded-full hover:bg-green-200"
                    >
                      Download
                    </button>
                    <button
                      onClick={() => handleDelete(file.cid)}
                      className="px-2 py-1 text-xs font-medium text-red-700 bg-red-100 rounded-full hover:bg-red-200"
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <p className="flex items-center text-sm text-gray-500">
                      Size: {file.metadata?.size || 'Unknown'}
                    </p>
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Dashboard;