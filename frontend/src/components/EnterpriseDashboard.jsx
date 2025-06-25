import { useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { useTheme } from '../contexts/ThemeContext';

function EnterpriseDashboard() {
  const { token, userRole } = useContext(AuthContext);
  const [enterpriseData, setEnterpriseData] = useState(null);
  const [recentFiles, setRecentFiles] = useState([]);
  const [stats, setStats] = useState({
    totalFiles: 0,
    totalStorage: 0,
    products: 0,
    batches: 0
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const { darkMode } = useTheme();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchEnterpriseData = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`${import.meta.env.VITE_API_URL}/enterprise/profile`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch enterprise data');
        }

        const data = await response.json();
        setEnterpriseData(data);
        
        // Fetch files
        const filesResponse = await fetch(`${import.meta.env.VITE_API_URL}/storage/files`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (filesResponse.ok) {
          const filesData = await filesResponse.json();
          setRecentFiles(filesData.slice(0, 5)); // Get the 5 most recent files
          
          // Calculate total storage
          const totalBytes = filesData.reduce((sum, file) => sum + (file.size || 0), 0);
          const totalStorage = (totalBytes / (1024 * 1024)).toFixed(2); // Convert to MB
          
          setStats({
            totalFiles: filesData.length,
            totalStorage,
            products: data.productCount || 0,
            batches: data.batchCount || 0
          });
        }

        setIsLoading(false);
      } catch (err) {
        console.error('Error fetching enterprise data:', err);
        setError('Failed to load enterprise dashboard data. Please try again later.');
        setIsLoading(false);
      }
    };

    if (token) {
      fetchEnterpriseData();
    }
  }, [token]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const navigateToModule = (module) => {
    navigate(`/enterprise/${module}`);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="loader">Loading...</div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-100 text-gray-900'}`}>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className={`text-3xl font-bold ${darkMode ? 'text-blue-400' : 'text-blue-700'}`}>
            {enterpriseData?.name ? `${enterpriseData.name} Dashboard` : 'Enterprise Dashboard'}
          </h1>
          <p className={`mt-2 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Welcome to your enterprise blockchain storage portal
          </p>
        </div>

        {/* Stats Dashboard */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className={`p-6 rounded-lg shadow ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
            <h3 className="text-lg font-semibold text-gray-500">Files</h3>
            <p className={`text-3xl font-bold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>{stats.totalFiles}</p>
          </div>
          <div className={`p-6 rounded-lg shadow ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
            <h3 className="text-lg font-semibold text-gray-500">Storage</h3>
            <p className={`text-3xl font-bold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>{stats.totalStorage} MB</p>
          </div>
          <div className={`p-6 rounded-lg shadow ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
            <h3 className="text-lg font-semibold text-gray-500">Products</h3>
            <p className={`text-3xl font-bold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>{stats.products}</p>
          </div>
          <div className={`p-6 rounded-lg shadow ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
            <h3 className="text-lg font-semibold text-gray-500">Batches</h3>
            <p className={`text-3xl font-bold ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>{stats.batches}</p>
          </div>
        </div>

        {/* Enterprise Modules */}
        <div className="mb-8">
          <h2 className={`text-xl font-semibold mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-800'}`}>
            Enterprise Modules
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button 
              onClick={() => navigateToModule('products')}
              className={`p-6 rounded-lg shadow text-left ${darkMode ? 'bg-gray-800 hover:bg-gray-700' : 'bg-white hover:bg-blue-50'} transition-colors`}
            >
              <h3 className={`text-lg font-semibold ${darkMode ? 'text-blue-400' : 'text-blue-700'}`}>
                Product Management
              </h3>
              <p className={`mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                Create and manage product definitions, specifications and certifications.
              </p>
            </button>
            
            <button 
              onClick={() => navigateToModule('inventory')}
              className={`p-6 rounded-lg shadow text-left ${darkMode ? 'bg-gray-800 hover:bg-gray-700' : 'bg-white hover:bg-blue-50'} transition-colors`}
            >
              <h3 className={`text-lg font-semibold ${darkMode ? 'text-blue-400' : 'text-blue-700'}`}>
                Inventory Management
              </h3>
              <p className={`mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                Track inventory levels, locations and movements with blockchain verifiability.
              </p>
            </button>
            
            <button 
              onClick={() => navigateToModule('traceability')}
              className={`p-6 rounded-lg shadow text-left ${darkMode ? 'bg-gray-800 hover:bg-gray-700' : 'bg-white hover:bg-blue-50'} transition-colors`}
            >
              <h3 className={`text-lg font-semibold ${darkMode ? 'text-blue-400' : 'text-blue-700'}`}>
                Traceability
              </h3>
              <p className={`mt-1 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                Track product journey through the supply chain with immutable record-keeping.
              </p>
            </button>
          </div>
        </div>

        {/* Recent Files */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className={`text-xl font-semibold ${darkMode ? 'text-gray-300' : 'text-gray-800'}`}>
              Recent Files
            </h2>
            <Link 
              to="/enterprise/files" 
              className={`text-sm ${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-500'}`}
            >
              View All Files →
            </Link>
          </div>
          
          {recentFiles.length > 0 ? (
            <div className={`overflow-x-auto rounded-lg shadow ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
              <table className="min-w-full">
                <thead>
                  <tr className={darkMode ? 'bg-gray-700' : 'bg-gray-50'}>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Type</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Uploaded</th>
                    <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">Size</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {recentFiles.map((file, index) => (
                    <tr key={index} className={`${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'} transition-colors`}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link 
                          to={`/enterprise/files/${file.file_hash}`}
                          className={`font-medium ${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-500'}`}
                        >
                          {file.file_name || file.filename || 'Unnamed File'}
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {file.file_type || file.content_type || 'Unknown'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {formatDate(file.upload_date || file.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {file.size ? `${(file.size / 1024).toFixed(2)} KB` : 'Unknown'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className={`p-6 rounded-lg shadow text-center ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
              <p className={`${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>No files uploaded yet</p>
              <Link 
                to="/enterprise/upload" 
                className={`inline-block mt-2 px-4 py-2 rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors`}
              >
                Upload Files
              </Link>
            </div>
          )}
        </div>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default EnterpriseDashboard;
