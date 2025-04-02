import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, createContext, useContext } from 'react';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import Navbar from './components/Navbar';

// Create Authentication Context
export const AuthContext = createContext(null);

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isConnected, setIsConnected] = useState(false);

  const login = (newToken) => {
    setToken(newToken);
    localStorage.setItem('token', newToken);
  };

  const logout = () => {
    setToken(null);
    setIsConnected(false);
    localStorage.removeItem('token');
  };

  return (
    <AuthContext.Provider value={{ token, login, logout, isConnected, setIsConnected }}>
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