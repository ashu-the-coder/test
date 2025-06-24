import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';

const EnterpriseWelcome = () => {
  const navigate = useNavigate();
  const { darkMode } = useTheme();

  const handleSignIn = () => {
    navigate('/login'); // Redirect to existing login system
  };

  const handleRegister = () => {
    navigate('/enterprise/register'); // Redirect to enterprise registration options
  };

  return (
    <div className={`flex flex-col items-center justify-center min-h-screen ${darkMode ? 'bg-gradient-to-br from-gray-800 to-gray-900' : 'bg-gradient-to-br from-blue-50 to-blue-200'}`}>
      <div className={`${darkMode ? 'bg-gray-800 text-white' : 'bg-white'} rounded-lg shadow-xl p-10 max-w-2xl w-full text-center transition-colors duration-200`}>
        <h1 className={`text-4xl font-bold mb-6 ${darkMode ? 'text-blue-400' : 'text-blue-700'}`}>Enterprise Decentralized Storage Solution</h1>
        
        <div className="mb-8">
          <p className={`text-lg mb-4 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
            Welcome to our enterprise-grade decentralized storage platform built for businesses of all sizes.
          </p>
          <p className={`text-md mb-4 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Leverage the power of blockchain and IPFS technology to secure your organization's most valuable data
            with unprecedented levels of security, redundancy, and accessibility.
          </p>
          <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Looking for individual solutions? <Link to="/login" className={`${darkMode ? 'text-blue-300' : 'text-blue-600'} hover:underline`}>Go to personal account →</Link>
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-blue-50'}`}>
            <h3 className={`text-lg font-semibold mb-2 ${darkMode ? 'text-blue-300' : 'text-blue-600'}`}>Enterprise Features</h3>
            <ul className={`text-left text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              <li className="mb-1">• Customizable storage policies</li>
              <li className="mb-1">• Advanced access control</li>
              <li className="mb-1">• Multi-user management</li>
              <li className="mb-1">• Enhanced security protocols</li>
            </ul>
          </div>
          <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-blue-50'}`}>
            <h3 className={`text-lg font-semibold mb-2 ${darkMode ? 'text-blue-300' : 'text-blue-600'}`}>Business Benefits</h3>
            <ul className={`text-left text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
              <li className="mb-1">• Reduce storage costs by up to 60%</li>
              <li className="mb-1">• Eliminate single points of failure</li>
              <li className="mb-1">• Compliance-ready audit trails</li>
              <li className="mb-1">• Seamless integration options</li>
            </ul>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            className={`py-3 px-8 rounded-md font-medium text-white ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-600 hover:bg-blue-700'} transition-colors duration-200 shadow-md`}
            onClick={handleSignIn}
          >
            Sign In
          </button>
          <button
            className={`py-3 px-8 rounded-md font-medium ${darkMode ? 'bg-gray-600 text-white hover:bg-gray-700' : 'bg-gray-200 text-blue-700 hover:bg-blue-100'} transition-colors duration-200 shadow-md`}
            onClick={handleRegister}
          >
            Register
          </button>
        </div>
      </div>
    </div>
  );
};

export default EnterpriseWelcome;
