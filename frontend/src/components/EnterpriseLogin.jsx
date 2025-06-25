import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { ethers } from 'ethers';
import { useTheme } from '../contexts/ThemeContext';

function EnterpriseLogin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [enterpriseId, setEnterpriseId] = useState('');
  const [error, setError] = useState('');
  const { login } = useContext(AuthContext);
  const { darkMode } = useTheme();
  const navigate = useNavigate();

  const connectWallet = async () => {
    try {
      if (!window.ethereum) {
        throw new Error('Please install MetaMask to use this application');
      }

      await window.ethereum.request({ method: 'eth_requestAccounts' });
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const address = await signer.getAddress();
      return address;
    } catch (err) {
      setError('Failed to connect wallet: ' + err.message);
      return false;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Connect wallet first
      const walletAddress = await connectWallet();
      if (!walletAddress) return;

      const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/enterprise/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          username, 
          password, 
          enterprise_id: enterpriseId,
          wallet_address: walletAddress 
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Parse JWT token to get user role
      const tokenParts = data.access_token.split('.');
      if (tokenParts.length === 3) {
        try {
          // Decode base64 payload
          const payload = JSON.parse(atob(tokenParts[1]));
          const role = payload.role || 'enterprise';
          
          // Pass role to login function
          login(data.access_token, role);
        } catch (e) {
          console.error('Error parsing token:', e);
          login(data.access_token, 'enterprise');
        }
      } else {
        login(data.access_token, 'enterprise');
      }
      
      // Redirect to the enterprise dashboard
      navigate('/enterprise/dashboard');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-200">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Enterprise Portal
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Sign in to your enterprise account
          </p>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            <Link
              to="/login"
              className="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300"
            >
              ← Back to Personal Account
            </Link>
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-3">
            <div>
              <label htmlFor="enterprise-id" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Enterprise ID
              </label>
              <input
                id="enterprise-id"
                name="enterpriseId"
                type="text"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:z-10 sm:text-sm transition-colors duration-200"
                placeholder="Your Enterprise ID"
                value={enterpriseId}
                onChange={(e) => setEnterpriseId(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:z-10 sm:text-sm transition-colors duration-200"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:z-10 sm:text-sm transition-colors duration-200"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          {error && (
            <div className="text-red-500 dark:text-red-400 text-sm text-center">{error}</div>
          )}

          <div>
            <button
              type="submit"
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors duration-200"
            >
              Sign in to Enterprise Portal
            </button>
          </div>
          
          <div className="text-center mt-4">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Don't have an enterprise account?{' '}
              <Link
                to="/enterprise/register"
                className="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300"
              >
                Register your enterprise
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default EnterpriseLogin;
