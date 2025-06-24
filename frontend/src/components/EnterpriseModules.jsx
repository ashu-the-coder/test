import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { useTheme } from '../contexts/ThemeContext';

const ModuleCard = ({ title, description, icon, path, enabled = true }) => {
  const { darkMode } = useTheme();
  const navigate = useNavigate();

  return (
    <div 
      onClick={() => enabled && navigate(path)}
      className={`
        ${enabled ? 'cursor-pointer hover:shadow-lg transform hover:-translate-y-1' : 'opacity-60 cursor-not-allowed'} 
        transition-all duration-300 rounded-xl overflow-hidden shadow-md 
        ${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-800'} 
        flex flex-col p-6
      `}
    >
      <div className={`text-4xl mb-4 ${enabled ? (darkMode ? 'text-blue-400' : 'text-blue-600') : 'text-gray-500'}`}>
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className={`text-sm mb-4 flex-grow ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>{description}</p>
      {!enabled && (
        <span className="text-xs py-1 px-2 bg-yellow-500 text-white rounded-md inline-block">Coming Soon</span>
      )}
      {enabled && (
        <span className={`text-sm ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>
          Access Module →
        </span>
      )}
    </div>
  );
};

function EnterpriseModules() {
  const { token } = useContext(AuthContext);
  const { darkMode } = useTheme();
  const navigate = useNavigate();

  // Redirect to login if not authenticated
  React.useEffect(() => {
    if (!token) {
      navigate('/login');
    }
  }, [token, navigate]);

  const modules = [
    {
      title: "Enterprise Registration",
      description: "Register and manage your enterprise account information, add company details and update credentials.",
      icon: "🏢",
      path: "/enterprise/profile",
      enabled: true
    },
    {
      title: "Product & Batch Management",
      description: "Create, view, edit, and manage products and production batches with detailed information and history.",
      icon: "📦",
      path: "/enterprise/products",
      enabled: true
    },
    {
      title: "Traceability",
      description: "Track product journey through the supply chain with event logging and verification at each step.",
      icon: "🔍",
      path: "/enterprise/traceability",
      enabled: true
    },
    {
      title: "Live Inventory Management",
      description: "Real-time inventory tracking, stock levels, warehouse management and automated alerts.",
      icon: "📊",
      path: "/enterprise/inventory",
      enabled: true
    },
    {
      title: "Audit Logging",
      description: "Comprehensive activity logging and auditing for compliance and security purposes.",
      icon: "📃",
      path: "/enterprise/audit",
      enabled: true
    },
    {
      title: "Access Control",
      description: "Define user roles, permissions, and access levels for your organization's team members.",
      icon: "🔐",
      path: "/enterprise/access",
      enabled: true
    },
    {
      title: "Blockchain/IPFS Integration",
      description: "Leverage blockchain for immutable records and IPFS for decentralized storage of critical data.",
      icon: "⛓️",
      path: "/enterprise/blockchain",
      enabled: true
    },
    {
      title: "QR Code Generation",
      description: "Generate and manage QR codes for product identification, verification, and tracking.",
      icon: "📱",
      path: "/enterprise/qr",
      enabled: true
    }
  ];

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900' : 'bg-gray-50'} transition-colors duration-200 py-10 px-4 sm:px-6 lg:px-8`}>
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className={`text-3xl font-extrabold ${darkMode ? 'text-white' : 'text-gray-900'} sm:text-4xl`}>
            Enterprise Management Suite
          </h1>
          <p className={`mt-3 max-w-2xl mx-auto text-xl ${darkMode ? 'text-gray-300' : 'text-gray-500'} sm:mt-4`}>
            Access all enterprise management modules from this central dashboard
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {modules.map((module, index) => (
            <ModuleCard key={index} {...module} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default EnterpriseModules;
