import { useState } from 'react';
import { useContext } from 'react';
import { AuthContext } from '../App';

const FileUpload = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [uploadResult, setUploadResult] = useState(null);
    const { token } = useContext(AuthContext);

    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setFile(e.target.files[0]);
            setUploadResult(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setUploadResult(null);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch(`${import.meta.env.VITE_API_URL}/storage/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                setUploadResult({
                    success: true,
                    message: 'File uploaded successfully!',
                    cid: data.cid,
                    txHash: data.tx_hash
                });
                if (onUploadSuccess) onUploadSuccess();
            } else {
                throw new Error(data.detail || 'Upload failed');
            }
        } catch (error) {
            setUploadResult({
                success: false,
                message: error.message
            });
        } finally {
            setUploading(false);
            setFile(null);
        }
    };

    return (
        <div className="p-6 bg-white rounded-lg shadow-md">
            <div className="mb-6">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                    Select File to Upload
                </label>
                <input
                    type="file"
                    onChange={handleFileChange}
                    className="hidden"
                    id="fileInput"
                    disabled={uploading}
                />
                <label
                    htmlFor="fileInput"
                    className={`cursor-pointer inline-block px-4 py-2 border rounded-md ${file ? 'bg-blue-50 border-blue-500 text-blue-600' : 'bg-gray-50 border-gray-300 text-gray-600'} hover:bg-blue-100 transition-colors`}
                >
                    {file ? file.name : 'Choose a file'}
                </label>
            </div>

            <button
                onClick={handleUpload}
                disabled={!file || uploading}
                className={`w-full py-2 px-4 rounded-md font-medium ${!file || uploading ? 'bg-gray-300 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600 text-white'} transition-colors`}
            >
                {uploading ? 'Uploading...' : 'Upload to IPFS'}
            </button>

            {uploadResult && (
                <div className={`mt-4 p-4 rounded-md ${uploadResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                    <p className={`text-sm ${uploadResult.success ? 'text-green-700' : 'text-red-700'}`}>
                        {uploadResult.message}
                    </p>
                    {uploadResult.success && (
                        <div className="mt-2 text-sm text-gray-600">
                            <p><span className="font-semibold">IPFS CID:</span> {uploadResult.cid}</p>
                            <p><span className="font-semibold">Transaction Hash:</span> {uploadResult.txHash}</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default FileUpload;