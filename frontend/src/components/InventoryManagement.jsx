import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { useTheme } from '../contexts/ThemeContext';

function InventoryManagement() {
  const { token } = useContext(AuthContext);
  const { darkMode } = useTheme();
  const navigate = useNavigate();
  
  const [products, setProducts] = useState([]);
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [selectedProduct, setSelectedProduct] = useState('');
  const [auditLogs, setAuditLogs] = useState([]);
  const [showAuditLogs, setShowAuditLogs] = useState(false);
  
  const [updateForm, setUpdateForm] = useState({
    product_id: '',
    location: '',
    change_in_quantity: '',
    operation: 'add',
    notes: ''
  });
  
  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    
    fetchProducts();
  }, [token, navigate]);
  
  const fetchProducts = async () => {
    try {
      const enterpriseId = localStorage.getItem('enterpriseId');
      if (!enterpriseId) {
        throw new Error('Enterprise ID not found');
      }
      
      const response = await fetch(`${import.meta.env.VITE_API_URL}/product/list/${enterpriseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch products');
      }
      
      const data = await response.json();
      setProducts(data);
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Failed to load products');
      
      // Mock data for demonstration
      setProducts([
        { id: 'prod_12345', product_name: 'Premium Widget', product_type: 'Hardware', unit: 'piece' },
        { id: 'prod_23456', product_name: 'Standard Gadget', product_type: 'Hardware', unit: 'piece' },
        { id: 'prod_34567', product_name: 'Organic Compound', product_type: 'Chemical', unit: 'liter' }
      ]);
    }
  };
  
  const fetchInventory = async (productId) => {
    setLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/inventory/${productId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch inventory');
      }
      
      const data = await response.json();
      setInventory(data);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching inventory:', err);
      setError('Failed to load inventory');
      setLoading(false);
      
      // Mock data for demonstration
      setInventory([
        { id: 'inv_12345', product_id: productId, location: 'Warehouse A', quantity: 500, last_updated: '2025-06-24T12:00:00' },
        { id: 'inv_23456', product_id: productId, location: 'Warehouse B', quantity: 350, last_updated: '2025-06-25T10:30:00' }
      ]);
    }
  };
  
  const fetchAuditLogs = async (productId) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/inventory/audit/${productId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch audit logs');
      }
      
      const data = await response.json();
      setAuditLogs(data);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
      
      // Mock data for demonstration
      setAuditLogs([
        { 
          id: 'log_12345', 
          product_id: productId, 
          location: 'Warehouse A', 
          previous_quantity: 400, 
          new_quantity: 500, 
          change_amount: 100, 
          operation: 'add', 
          timestamp: '2025-06-24T12:00:00',
          notes: 'Initial stock'
        },
        { 
          id: 'log_23456', 
          product_id: productId, 
          location: 'Warehouse B', 
          previous_quantity: 350, 
          new_quantity: 300, 
          change_amount: 50, 
          operation: 'remove', 
          timestamp: '2025-06-25T10:30:00',
          notes: 'Shipped to customer'
        }
      ]);
    }
  };
  
  const handleProductChange = (e) => {
    const productId = e.target.value;
    setSelectedProduct(productId);
    setUpdateForm({
      ...updateForm,
      product_id: productId
    });
    if (productId) {
      fetchInventory(productId);
      setShowAuditLogs(false);
    } else {
      setInventory([]);
      setAuditLogs([]);
    }
  };
  
  const handleUpdateFormChange = (e) => {
    const { name, value } = e.target;
    setUpdateForm({
      ...updateForm,
      [name]: name === 'change_in_quantity' ? parseFloat(value) || '' : value
    });
  };
  
  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    
    // Basic form validation
    if (!updateForm.product_id || !updateForm.location || !updateForm.change_in_quantity) {
      setFormError('Please fill in all required fields');
      return;
    }
    
    if (updateForm.change_in_quantity <= 0) {
      setFormError('Change in quantity must be positive');
      return;
    }
    
    setFormError('');
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/inventory/update`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(updateForm)
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to update inventory');
      }
      
      // Refresh inventory after update
      fetchInventory(updateForm.product_id);
      
      // Reset form
      setUpdateForm({
        product_id: updateForm.product_id,
        location: '',
        change_in_quantity: '',
        operation: 'add',
        notes: ''
      });
      
    } catch (err) {
      console.error('Error updating inventory:', err);
      setFormError(err.message || 'Failed to update inventory');
    }
  };
  
  const toggleAuditLogs = () => {
    if (!showAuditLogs && selectedProduct) {
      fetchAuditLogs(selectedProduct);
    }
    setShowAuditLogs(!showAuditLogs);
  };
  
  return (
    <div className={`p-6 ${darkMode ? 'bg-gray-900 text-gray-100' : 'bg-white text-gray-900'}`}>
      <div className="mb-10 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Inventory Management</h1>
        <div className="flex space-x-4">
          <button
            onClick={() => navigate('/enterprise/modules')}
            className={`px-4 py-2 rounded-md ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'} transition duration-200`}
          >
            Back to Modules
          </button>
          <button
            onClick={() => navigate('/enterprise/products')}
            className={`px-4 py-2 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200`}
          >
            Batch Management
          </button>
        </div>
      </div>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}
      
      <div className={`mb-6 p-4 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}>
        <h2 className="text-xl font-semibold mb-4">Update Inventory</h2>
        
        <form onSubmit={handleUpdateSubmit}>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                Product <span className="text-red-500">*</span>
              </label>
              <select
                value={updateForm.product_id}
                onChange={handleProductChange}
                className={`w-full px-3 py-2 border rounded-md ${
                  darkMode 
                    ? 'bg-gray-700 border-gray-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
                } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                required
              >
                <option value="">Select a product</option>
                {products.map(product => (
                  <option key={product.id} value={product.id}>
                    {product.product_name} ({product.product_type})
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                Location <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="location"
                value={updateForm.location}
                onChange={handleUpdateFormChange}
                placeholder="e.g. Warehouse A, Store #123"
                className={`w-full px-3 py-2 border rounded-md ${
                  darkMode 
                    ? 'bg-gray-700 border-gray-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
                } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                required
              />
            </div>
            
            <div>
              <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                Quantity Change <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                step="0.01"
                name="change_in_quantity"
                value={updateForm.change_in_quantity}
                onChange={handleUpdateFormChange}
                className={`w-full px-3 py-2 border rounded-md ${
                  darkMode 
                    ? 'bg-gray-700 border-gray-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
                } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                required
              />
            </div>
            
            <div>
              <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                Operation <span className="text-red-500">*</span>
              </label>
              <select
                name="operation"
                value={updateForm.operation}
                onChange={handleUpdateFormChange}
                className={`w-full px-3 py-2 border rounded-md ${
                  darkMode 
                    ? 'bg-gray-700 border-gray-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
                } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                required
              >
                <option value="add">Add to inventory</option>
                <option value="remove">Remove from inventory</option>
              </select>
            </div>
            
            <div className="md:col-span-2">
              <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                Notes
              </label>
              <textarea
                name="notes"
                rows="2"
                value={updateForm.notes}
                onChange={handleUpdateFormChange}
                className={`w-full px-3 py-2 border rounded-md ${
                  darkMode 
                    ? 'bg-gray-700 border-gray-600 text-white' 
                    : 'bg-white border-gray-300 text-gray-900'
                } focus:outline-none focus:ring-2 focus:ring-blue-500`}
              ></textarea>
            </div>
          </div>
          
          {formError && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              <p>{formError}</p>
            </div>
          )}
          
          <div className="mt-4">
            <button
              type="submit"
              className={`px-5 py-2 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200`}
            >
              Update Inventory
            </button>
          </div>
        </form>
      </div>
      
      {selectedProduct && (
        <>
          <div className={`mb-6 p-4 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Current Inventory</h2>
              <button
                onClick={toggleAuditLogs}
                className={`px-3 py-1 rounded-md ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'} transition duration-200`}
              >
                {showAuditLogs ? 'Hide Audit Trail' : 'Show Audit Trail'}
              </button>
            </div>
            
            {loading ? (
              <p>Loading inventory data...</p>
            ) : inventory.length > 0 ? (
              <div className="overflow-x-auto">
                <table className={`min-w-full ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                  <thead>
                    <tr className={darkMode ? 'bg-gray-700' : 'bg-gray-200'}>
                      <th className="px-4 py-2 text-left">Location</th>
                      <th className="px-4 py-2 text-left">Quantity</th>
                      <th className="px-4 py-2 text-left">Last Updated</th>
                    </tr>
                  </thead>
                  <tbody>
                    {inventory.map(item => (
                      <tr key={item.id} className={darkMode ? 'border-b border-gray-700' : 'border-b border-gray-200'}>
                        <td className="px-4 py-2">{item.location}</td>
                        <td className="px-4 py-2">{item.quantity.toLocaleString()}</td>
                        <td className="px-4 py-2">
                          {new Date(item.last_updated).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p>No inventory found for this product.</p>
            )}
          </div>
          
          {showAuditLogs && (
            <div className={`mb-6 p-4 rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}>
              <h2 className="text-xl font-semibold mb-4">Audit Trail</h2>
              
              {auditLogs.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className={`min-w-full ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                    <thead>
                      <tr className={darkMode ? 'bg-gray-700' : 'bg-gray-200'}>
                        <th className="px-4 py-2 text-left">Timestamp</th>
                        <th className="px-4 py-2 text-left">Location</th>
                        <th className="px-4 py-2 text-left">Operation</th>
                        <th className="px-4 py-2 text-left">Change</th>
                        <th className="px-4 py-2 text-left">From</th>
                        <th className="px-4 py-2 text-left">To</th>
                        <th className="px-4 py-2 text-left">Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {auditLogs.map(log => (
                        <tr key={log.id} className={darkMode ? 'border-b border-gray-700' : 'border-b border-gray-200'}>
                          <td className="px-4 py-2">{new Date(log.timestamp).toLocaleString()}</td>
                          <td className="px-4 py-2">{log.location}</td>
                          <td className="px-4 py-2">
                            <span className={`px-2 py-1 rounded text-xs ${
                              log.operation === 'add' 
                                ? (darkMode ? 'bg-green-800 text-green-200' : 'bg-green-100 text-green-800')
                                : (darkMode ? 'bg-red-800 text-red-200' : 'bg-red-100 text-red-800')
                            }`}>
                              {log.operation}
                            </span>
                          </td>
                          <td className="px-4 py-2">
                            {log.operation === 'add' ? '+' : '-'}{log.change_amount.toLocaleString()}
                          </td>
                          <td className="px-4 py-2">{log.previous_quantity.toLocaleString()}</td>
                          <td className="px-4 py-2">{log.new_quantity.toLocaleString()}</td>
                          <td className="px-4 py-2">{log.notes || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p>No audit logs found for this product.</p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default InventoryManagement;
