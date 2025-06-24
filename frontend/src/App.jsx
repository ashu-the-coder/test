import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, createContext, useContext, useEffect } from 'react';
import { ethers } from 'ethers';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Profile from './components/Profile';
import Navbar from './components/Navbar';
import EnterpriseWelcome from './components/EnterpriseWelcome';
import EnterpriseRegister from './components/EnterpriseRegister';
import EnterpriseModules from './components/EnterpriseModules';
import EnterpriseProfile from './components/EnterpriseProfile';
import ProductManagement from './components/ProductManagement';
import BatchManagement from './components/BatchManagement';
import Traceability from './components/Traceability';
import InventoryManagement from './components/InventoryManagement';
import { ThemeProvider } from './contexts/ThemeContext';

// Create Authentication Context
export const AuthContext = createContext(null);

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isConnected, setIsConnected] = useState(localStorage.getItem('walletConnected') === 'true');
  const [userAddress, setUserAddress] = useState(localStorage.getItem('userAddress'));
  const [userRole, setUserRole] = useState(localStorage.getItem('userRole') || 'individual');

  useEffect(() => {
    const checkWalletConnection = async () => {
      try {
        if (window.ethereum) {
          const accounts = await window.ethereum.request({ method: 'eth_accounts' });
          const isConnected = accounts.length > 0;
          setIsConnected(isConnected);
          localStorage.setItem('walletConnected', isConnected);
          
          if (isConnected && accounts[0]) {
            setUserAddress(accounts[0]);
            localStorage.setItem('userAddress', accounts[0]);
          } else {
            setUserAddress(null);
            localStorage.removeItem('userAddress');
          }
        }
      } catch (error) {
        console.error('Error checking wallet connection:', error);
        setIsConnected(false);
        setUserAddress(null);
        localStorage.setItem('walletConnected', 'false');
        localStorage.removeItem('userAddress');
      }
    };

    checkWalletConnection();

    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts) => {
        const isConnected = accounts.length > 0;
        setIsConnected(isConnected);
        localStorage.setItem('walletConnected', isConnected);
        
        if (isConnected && accounts[0]) {
          setUserAddress(accounts[0]);
          localStorage.setItem('userAddress', accounts[0]);
        } else {
          setUserAddress(null);
          localStorage.removeItem('userAddress');
        }
      });

      window.ethereum.on('disconnect', () => {
        setIsConnected(false);
        setUserAddress(null);
        localStorage.setItem('walletConnected', 'false');
        localStorage.removeItem('userAddress');
      });
    }
  }, []);

  const login = async (newToken, role = 'individual') => {
    setToken(newToken);
    localStorage.setItem('token', newToken);
    
    // Set user role
    setUserRole(role);
    localStorage.setItem('userRole', role);
    
    // Check wallet connection on login
    if (window.ethereum) {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        const isConnected = accounts.length > 0;
        setIsConnected(isConnected);
        localStorage.setItem('walletConnected', isConnected);
        
        if (isConnected && accounts[0]) {
          setUserAddress(accounts[0]);
          localStorage.setItem('userAddress', accounts[0]);
        }
      } catch (error) {
        console.error('Error checking wallet connection:', error);
      }
    }
  };

  const logout = () => {
    setToken(null);
    setIsConnected(false);
    setUserAddress(null);
    setUserRole('individual');
    localStorage.removeItem('token');
    localStorage.removeItem('userAddress');
    localStorage.removeItem('userRole');
  };

  return (
    <ThemeProvider>
      <AuthContext.Provider value={{ token, login, logout, isConnected, setIsConnected, userAddress, userRole }}>
        <Router>
          <div className="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-200">
            {token && <Navbar />}
            <Routes>
              <Route
                path="/login"
                element={
                  !token ? (
                    <Login />
                  ) : (
                    <Navigate to="/dashboard" replace />
                  )
                }
              />
              <Route
                path="/register"
                element={
                  !token ? (
                    <Register />
                  ) : (
                    <Navigate to="/dashboard" replace />
                  )
                }
              />
              <Route
                path="/dashboard"
                element={
                  token ? (
                    <Dashboard />
                  ) : (
                    <Navigate to="/login" replace />
                  )
                }
              />
              <Route
                path="/profile"
                element={
                  token ? (
                    <Profile />
                  ) : (
                    <Navigate to="/login" replace />
                  )
                }
              />
              <Route path="/enterprise" element={<EnterpriseWelcome />} />
              <Route path="/enterprise/register" element={<EnterpriseRegister />} />
              <Route
                path="/enterprise/modules"
                element={
                  token ? <EnterpriseModules /> : <Navigate to="/login" replace />
                }
              />
              <Route
                path="/enterprise/profile"
                element={
                  token ? <EnterpriseProfile /> : <Navigate to="/login" replace />
                }
              />
              <Route
                path="/enterprise/products"
                element={
                  token ? <ProductManagement /> : <Navigate to="/login" replace />
                }
              />
              <Route
                path="/enterprise/traceability"
                element={
                  token ? <Traceability /> : <Navigate to="/login" replace />
                }
              />
              <Route
                path="/enterprise/inventory"
                element={
                  token ? <InventoryManagement /> : <Navigate to="/login" replace />
                }
              />
              <Route path="/" element={<Navigate to="/login" replace />} />
            </Routes>
          </div>
        </Router>
      </AuthContext.Provider>
    </ThemeProvider>
  );
}

export default App;