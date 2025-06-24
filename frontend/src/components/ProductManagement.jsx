import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { useTheme } from '../contexts/ThemeContext';

function ProductManagement() {
  const { token } = useContext(AuthContext);
  const { darkMode } = useTheme();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState('products');
  const [products, setProducts] = useState([]);
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [showProductForm, setShowProductForm] = useState(false);
  const [showBatchForm, setShowBatchForm] = useState(false);
  
  const [productForm, setProductForm] = useState({
    product_name: '',
    product_code: '',
    description: '',
    category: '',
    unit: '',
    price: ''
  });
  
  const [batchForm, setBatchForm] = useState({
    batch_number: '',
    product_id: '',
    production_date: '',
    expiry_date: '',
    quantity: '',
    status: 'produced' 
  });
  
  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    
    fetchProductData();
  }, [token, navigate]);
  
  const fetchProductData = async () => {
    setLoading(true);
    try {
      const enterpriseId = localStorage.getItem('enterpriseId');
      if (!enterpriseId) {
        throw new Error('Enterprise ID not found');
      }
      
      // Fetch products for the enterprise from API
      const productsResponse = await fetch(`${import.meta.env.VITE_API_URL}/product/list/${enterpriseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!productsResponse.ok) {
        const errorData = await productsResponse.json();
        throw new Error(errorData.detail || 'Failed to fetch products');
      }
      
      const productsData = await productsResponse.json();
      setProducts(productsData);
      
      // For now, we'll still use mock batch data until the batch endpoints are implemented
      const mockBatches = [
        { id: '1', batch_number: 'BATCH-001', product_id: productsData[0]?.id || '1', product_name: productsData[0]?.product_name || 'Product', production_date: '2025-05-01', expiry_date: '2027-05-01', quantity: 1000, status: 'shipped' },
        { id: '2', batch_number: 'BATCH-002', product_id: productsData[0]?.id || '1', product_name: productsData[0]?.product_name || 'Product', production_date: '2025-06-01', expiry_date: '2027-06-01', quantity: 2500, status: 'in_storage' },
      ];
      
      setBatches(mockBatches);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching product data:', err);
      
      // Fallback to mock data if API call fails
      const mockProducts = [
        { id: 'prod_mock1', product_name: 'Premium Widget', product_type: 'Hardware', description: 'High quality widget for industrial use', unit: 'piece' },
        { id: 'prod_mock2', product_name: 'Standard Gadget', product_type: 'Hardware', description: 'Reliable gadget for everyday use', unit: 'piece' },
        { id: 'prod_mock3', product_name: 'Organic Compound', product_type: 'Chemical', description: 'Natural organic compound', unit: 'liter' }
      ];
      
      const mockBatches = [
        { id: '1', batch_number: 'WID-001-B1', product_id: 'prod_mock1', product_name: 'Premium Widget', production_date: '2025-05-01', expiry_date: '2027-05-01', quantity: 1000, status: 'shipped' },
        { id: '2', batch_number: 'GAD-001-B1', product_id: 'prod_mock2', product_name: 'Standard Gadget', production_date: '2025-06-01', expiry_date: '2027-06-01', quantity: 2500, status: 'in_storage' },
        { id: '3', batch_number: 'ORG-001-B1', product_id: 'prod_mock3', product_name: 'Organic Compound', production_date: '2025-06-15', expiry_date: '2026-06-15', quantity: 500, status: 'produced' }
      ];
      
      setProducts(mockProducts);
      setBatches(mockBatches);
      setError('Failed to load product data from server. Displaying mock data.');
      setLoading(false);
    }
  };
  
  const handleProductFormChange = (e) => {
    const { name, value } = e.target;
    setProductForm({
      ...productForm,
      [name]: name === 'price' ? parseFloat(value) || '' : value
    });
  };
  
  const handleBatchFormChange = (e) => {
    const { name, value } = e.target;
    setBatchForm({
      ...batchForm,
      [name]: name === 'quantity' ? parseInt(value) || '' : value
    });
  };
  
  const handleProductSubmit = async (e) => {
    e.preventDefault();
    try {
      const enterpriseId = localStorage.getItem('enterpriseId');
      if (!enterpriseId) {
        throw new Error('Enterprise ID not found');
      }
      
      // Call the API to add a new product
      const response = await fetch(`${import.meta.env.VITE_API_URL}/product/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          enterprise_id: enterpriseId,
          product_name: productForm.product_name,
          product_type: productForm.category || 'General', // Map category to product_type
          unit: productForm.unit,
          description: productForm.description,
          sku: productForm.product_code // Map product_code to sku
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to add product');
      }
      
      // Refresh product list after successful addition
      fetchProductData();
      
      // Reset form
      setProductForm({
        product_name: '',
        product_code: '',
        description: '',
        category: '',
        unit: '',
        price: ''
      });
      setShowProductForm(false);
      
    } catch (err) {
      console.error('Error adding product:', err);
      setError(err.message || 'Failed to add product');
    }
  };
  
  const handleBatchSubmit = async (e) => {
    e.preventDefault();
    // Find the associated product for product_name
    const product = products.find(p => p.id === batchForm.product_id);
    
    // In production, this would be an API call to create/update a batch
    const newBatch = {
      id: Math.random().toString(36).substring(2, 9),
      ...batchForm,
      product_name: product ? product.product_name : 'Unknown Product'
    };
    
    setBatches([...batches, newBatch]);
    setBatchForm({
      batch_number: '',
      product_id: '',
      production_date: '',
      expiry_date: '',
      quantity: '',
      status: 'produced'
    });
    setShowBatchForm(false);
  };
  
  const getStatusBadgeColor = (status) => {
    switch(status) {
      case 'produced':
        return darkMode ? 'bg-yellow-700 text-yellow-100' : 'bg-yellow-100 text-yellow-800';
      case 'in_storage':
        return darkMode ? 'bg-blue-700 text-blue-100' : 'bg-blue-100 text-blue-800';
      case 'shipped':
        return darkMode ? 'bg-green-700 text-green-100' : 'bg-green-100 text-green-800';
      case 'sold':
        return darkMode ? 'bg-purple-700 text-purple-100' : 'bg-purple-100 text-purple-800';
      default:
        return darkMode ? 'bg-gray-700 text-gray-100' : 'bg-gray-100 text-gray-800';
    }
  };
  
  if (loading) {
    return (
      <div className={`min-h-screen flex items-center justify-center ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'}`}>
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-900'} transition-colors duration-200 py-10 px-4 sm:px-6 lg:px-8`}>
      <div className="max-w-7xl mx-auto">
        <div className="mb-10 flex justify-between items-center">
          <h1 className="text-3xl font-bold">Product & Batch Management</h1>
          <button
            onClick={() => navigate('/enterprise/modules')}
            className={`px-4 py-2 rounded-md ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-200 hover:bg-gray-300'} transition duration-200`}
          >
            Back to Modules
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-100 border-l-4 border-red-500 text-red-700 dark:bg-red-900 dark:text-red-300">
            {error}
          </div>
        )}
        
        {/* Tabs */}
        <div className="mb-6 border-b border-gray-200 dark:border-gray-700">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('products')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'products'
                  ? `${darkMode ? 'border-blue-400 text-blue-400' : 'border-blue-500 text-blue-600'}`
                  : `${darkMode ? 'border-transparent text-gray-400 hover:text-gray-300' : 'border-transparent text-gray-500 hover:text-gray-700'}`
              }`}
            >
              Products
            </button>
            <button
              onClick={() => setActiveTab('batches')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'batches'
                  ? `${darkMode ? 'border-blue-400 text-blue-400' : 'border-blue-500 text-blue-600'}`
                  : `${darkMode ? 'border-transparent text-gray-400 hover:text-gray-300' : 'border-transparent text-gray-500 hover:text-gray-700'}`
              }`}
            >
              Batches
            </button>
          </nav>
        </div>
        
        {/* Products Tab */}
        {activeTab === 'products' && (
          <div>
            <div className="mb-6 flex justify-end">
              <button
                onClick={() => setShowProductForm(!showProductForm)}
                className={`px-4 py-2 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200 flex items-center`}
              >
                <span className="mr-2">
                  {showProductForm ? 'Cancel' : 'Add Product'}
                </span>
                {!showProductForm && <span>+</span>}
              </button>
            </div>
            
            {showProductForm && (
              <div className={`mb-8 p-6 rounded-md shadow-md ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
                <h2 className="text-xl font-semibold mb-4">Add New Product</h2>
                <form onSubmit={handleProductSubmit}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Product Name
                      </label>
                      <input
                        type="text"
                        name="product_name"
                        value={productForm.product_name}
                        onChange={handleProductFormChange}
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
                        Product Code
                      </label>
                      <input
                        type="text"
                        name="product_code"
                        value={productForm.product_code}
                        onChange={handleProductFormChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                        required
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Description
                      </label>
                      <textarea
                        name="description"
                        value={productForm.description}
                        onChange={handleProductFormChange}
                        rows="3"
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                        required
                      ></textarea>
                    </div>
                    <div>
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Category
                      </label>
                      <input
                        type="text"
                        name="category"
                        value={productForm.category}
                        onChange={handleProductFormChange}
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
                        Unit
                      </label>
                      <input
                        type="text"
                        name="unit"
                        value={productForm.unit}
                        onChange={handleProductFormChange}
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
                        Price
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        name="price"
                        value={productForm.price}
                        onChange={handleProductFormChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                        required
                      />
                    </div>
                  </div>
                  <div className="mt-6">
                    <button
                      type="submit"
                      className={`px-5 py-2 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200`}
                    >
                      Save Product
                    </button>
                  </div>
                </form>
              </div>
            )}
            
            {/* Products Table */}
            <div className={`overflow-x-auto rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} shadow-md`}>
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className={`${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Product Name
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      SKU
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Type
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Unit
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Created
                    </th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {products.length > 0 ? (
                    products.map((product) => (
                      <tr key={product.id} className={`${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'}`}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-medium">{product.product_name}</div>
                          <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} truncate max-w-[200px]`}>
                            {product.description}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {product.sku || product.product_code || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {product.product_type || product.category || 'General'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {product.unit}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {product.creation_date ? new Date(product.creation_date).toLocaleDateString() : 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button className={`${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-900'} mr-3`}>
                            Edit
                          </button>
                          <button className={`${darkMode ? 'text-red-400 hover:text-red-300' : 'text-red-600 hover:text-red-900'}`}>
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="6" className="px-6 py-4 text-center">
                        No products found. Add your first product.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
        
        {/* Batches Tab */}
        {activeTab === 'batches' && (
          <div>
            <div className="mb-6 flex justify-end">
              <button
                onClick={() => setShowBatchForm(!showBatchForm)}
                className={`px-4 py-2 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200 flex items-center`}
              >
                <span className="mr-2">
                  {showBatchForm ? 'Cancel' : 'Add Batch'}
                </span>
                {!showBatchForm && <span>+</span>}
              </button>
            </div>
            
            {showBatchForm && (
              <div className={`mb-8 p-6 rounded-md shadow-md ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
                <h2 className="text-xl font-semibold mb-4">Add New Batch</h2>
                <form onSubmit={handleBatchSubmit}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Batch Number
                      </label>
                      <input
                        type="text"
                        name="batch_number"
                        value={batchForm.batch_number}
                        onChange={handleBatchFormChange}
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
                        Product
                      </label>
                      <select
                        name="product_id"
                        value={batchForm.product_id}
                        onChange={handleBatchFormChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                        required
                      >
                        <option value="">Select Product</option>
                        {products.map(product => (
                          <option key={product.id} value={product.id}>
                            {product.product_name} ({product.product_code})
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Production Date
                      </label>
                      <input
                        type="date"
                        name="production_date"
                        value={batchForm.production_date}
                        onChange={handleBatchFormChange}
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
                        Expiry Date
                      </label>
                      <input
                        type="date"
                        name="expiry_date"
                        value={batchForm.expiry_date}
                        onChange={handleBatchFormChange}
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
                        Quantity
                      </label>
                      <input
                        type="number"
                        name="quantity"
                        value={batchForm.quantity}
                        onChange={handleBatchFormChange}
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
                        Status
                      </label>
                      <select
                        name="status"
                        value={batchForm.status}
                        onChange={handleBatchFormChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                        required
                      >
                        <option value="produced">Produced</option>
                        <option value="in_storage">In Storage</option>
                        <option value="shipped">Shipped</option>
                        <option value="sold">Sold</option>
                      </select>
                    </div>
                  </div>
                  <div className="mt-6">
                    <button
                      type="submit"
                      className={`px-5 py-2 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200`}
                    >
                      Save Batch
                    </button>
                  </div>
                </form>
              </div>
            )}
            
            {/* Batches Table */}
            <div className={`overflow-x-auto rounded-lg ${darkMode ? 'bg-gray-800' : 'bg-white'} shadow-md`}>
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className={`${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Batch Number
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Product
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Production Date
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Expiry Date
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Quantity
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Status
                    </th>
                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {batches.length > 0 ? (
                    batches.map((batch) => (
                      <tr key={batch.id} className={`${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'}`}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {batch.batch_number}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {batch.product_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {batch.production_date}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {batch.expiry_date}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          {batch.quantity}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeColor(batch.status)}`}>
                            {batch.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button className={`${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-900'} mr-3`}>
                            Edit
                          </button>
                          <button className={`${darkMode ? 'text-red-400 hover:text-red-300' : 'text-red-600 hover:text-red-900'} mr-3`}>
                            Delete
                          </button>
                          <button className={`${darkMode ? 'text-green-400 hover:text-green-300' : 'text-green-600 hover:text-green-900'}`}>
                            QR Code
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="7" className="px-6 py-4 text-center">
                        No batches found. Add your first batch.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProductManagement;
