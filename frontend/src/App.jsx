import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, createContext, useContext, useEffect } from 'react';
import { ethers } from 'ethers';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Navbar from './components/Navbar';

// Create Authentication Context
export const AuthContext = createContext(null);

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isConnected, setIsConnected] = useState(localStorage.getItem('walletConnected') === 'true');
  const [userAddress, setUserAddress] = useState(localStorage.getItem('userAddress'));

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

  const login = async (newToken) => {
    setToken(newToken);
    localStorage.setItem('token', newToken);
    
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
    localStorage.removeItem('token');
    localStorage.removeItem('userAddress');
  };

  return (
    <AuthContext.Provider value={{ token, login, logout, isConnected, setIsConnected, userAddress }}>
      <Router>
        <div className="min-h-screen bg-gray-100">
          {token && <Navbar />}
          <div className="container mx-auto px-4 py-8">
            <Routes>
              <Route
                path="/"
                element={
                  token ? (
                    <Navigate to="/dashboard" />
                  ) : (
                    <Navigate to="/login" />
                  )
                }
              />
              <Route
                path="/login"
                element={
                  token ? <Navigate to="/dashboard" /> : <Login />
                }
              />
              <Route
                path="/register"
                element={
                  token ? <Navigate to="/dashboard" /> : <Register />
                }
              />
              <Route
                path="/dashboard"
                element={
                  token ? <Dashboard /> : <Navigate to="/login" />
                }
              />
            </Routes>
          </div>
        </div>
      </Router>
    </AuthContext.Provider>
  );
}

export default App;