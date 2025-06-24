import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { useTheme } from '../contexts/ThemeContext';

function Traceability() {
  const { token } = useContext(AuthContext);
  const { darkMode } = useTheme();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [batches, setBatches] = useState([]);
  const [events, setEvents] = useState([]);
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [showEventForm, setShowEventForm] = useState(false);
  
  const [eventForm, setEventForm] = useState({
    batch_id: '',
    event_type: '',
    location: '',
    temperature: '',
    humidity: '',
    operator: '',
    notes: '',
    ipfs_cid: '',
  });
  
  const [eventFile, setEventFile] = useState(null);

  // Validation function for IPFS CID
  const isValidIpfsCid = (cid) => {
    if (!cid) return false;
    // Basic validation for CIDv0 (Qm...) or CIDv1 (bafy...)
    return cid.startsWith('Qm') || cid.startsWith('bafy');
  };
  
  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    
    fetchTraceabilityData();
  }, [token, navigate]);
  
  const fetchTraceabilityData = async () => {
    setLoading(true);
    try {
      const enterpriseId = localStorage.getItem('enterpriseId');
      if (!enterpriseId) {
        throw new Error('Enterprise ID not found');
      }
      
      // Fetch batches from the API
      const batchesResponse = await fetch(`${import.meta.env.VITE_API_URL}/batch/list/${enterpriseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!batchesResponse.ok) {
        const errorData = await batchesResponse.json();
        throw new Error(errorData.detail || 'Failed to fetch batches');
      }
      
      const batchesData = await batchesResponse.json();
      
      // Add product names to batches by fetching products
      const productsResponse = await fetch(`${import.meta.env.VITE_API_URL}/product/list/${enterpriseId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      let productsData = [];
      if (productsResponse.ok) {
        productsData = await productsResponse.json();
      }
      
      // Create a map of product_id to product_name
      const productMap = {};
      productsData.forEach(product => {
        productMap[product.id] = product.product_name;
      });
      
      // Add product_name to each batch
      const batchesWithProductNames = batchesData.map(batch => ({
        ...batch,
        product_name: productMap[batch.product_id] || 'Unknown Product',
        quantity: batch.current_quantity
      }));
      
      // If no batches are found or there's an error, use mock data for demonstration
      if (batchesWithProductNames.length === 0) {
        const mockBatches = [
          { id: 'batch_mock1', batch_number: 'WID-001-B1', product_id: '1', product_name: 'Premium Widget', production_date: '2025-05-01', expiry_date: '2027-05-01', quantity: 1000, status: 'shipped' },
          { id: 'batch_mock2', batch_number: 'GAD-001-B1', product_id: '2', product_name: 'Standard Gadget', production_date: '2025-06-01', expiry_date: '2027-06-01', quantity: 2500, status: 'in_storage' },
          { id: 'batch_mock3', batch_number: 'ORG-001-B1', product_id: '3', product_name: 'Organic Compound', production_date: '2025-06-15', expiry_date: '2026-06-15', quantity: 500, status: 'produced' }
        ];
        setBatches(mockBatches);
      } else {
        setBatches(batchesWithProductNames);
      }
      
      // Don't fetch events until a batch is selected
      setEvents([]);
      setSelectedBatch(null);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching traceability data:', err);
      
      // Fallback to mock data if API call fails
      const mockBatches = [
        { id: 'batch_mock1', batch_number: 'WID-001-B1', product_id: '1', product_name: 'Premium Widget', production_date: '2025-05-01', expiry_date: '2027-05-01', quantity: 1000, status: 'shipped' },
        { id: 'batch_mock2', batch_number: 'GAD-001-B1', product_id: '2', product_name: 'Standard Gadget', production_date: '2025-06-01', expiry_date: '2027-06-01', quantity: 2500, status: 'in_storage' },
        { id: 'batch_mock3', batch_number: 'ORG-001-B1', product_id: '3', product_name: 'Organic Compound', production_date: '2025-06-15', expiry_date: '2026-06-15', quantity: 500, status: 'produced' }
      ];
      
      const mockEvents = [
        { id: 'trace_mock1', batch_id: 'batch_mock1', batch_number: 'WID-001-B1', event_type: 'production', timestamp: '2025-05-01T08:30:00', location: 'Factory A', temperature: 22, humidity: 45, operator: 'John Smith', notes: 'Initial production run', blockchain_tx_hash: '0x1a2b3c...' },
        { id: 'trace_mock2', batch_id: 'batch_mock1', batch_number: 'WID-001-B1', event_type: 'quality_check', timestamp: '2025-05-01T14:15:00', location: 'Factory A QC Lab', temperature: 21, humidity: 43, operator: 'Jane Doe', notes: 'All tests passed', blockchain_tx_hash: '0x4d5e6f...' }
      ];
      
      setBatches(mockBatches);
      setEvents(mockEvents);
      setError('Failed to load traceability data from server. Displaying mock data.');
      setLoading(false);
    }
  };
  
  const handleEventFormChange = (e) => {
    const { name, value } = e.target;
    setEventForm({
      ...eventForm,
      [name]: name === 'temperature' || name === 'humidity' ? parseFloat(value) || '' : value
    });
  };
  
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setEventFile(e.target.files[0]);
    }
  };
  
  const uploadEventDocument = async (batchId) => {
    if (!eventFile) return null;
    
    try {
      const formData = new FormData();
      formData.append('file', eventFile);
      
      const uploadResponse = await fetch(`${import.meta.env.VITE_API_URL}/trace/upload?batch_id=${batchId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
      
      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json();
        throw new Error(errorData.detail || 'Failed to upload document');
      }
      
      const uploadData = await uploadResponse.json();
      return uploadData.ipfs_cid;
    } catch (err) {
      console.error('Error uploading document:', err);
      return null;
    }
  };
  
  const handleEventSubmit = async (e) => {
    e.preventDefault();
    
    // Basic form validation
    if (!eventForm.batch_id || !eventForm.event_type || !eventForm.location || !eventForm.operator) {
      setFormError('Please fill in all required fields');
      return;
    }
    
    // Either a file must be uploaded or a valid IPFS CID must be provided
    if (!eventFile && !eventForm.ipfs_cid) {
      setFormError('Either upload a document or provide an IPFS CID');
      return;
    }
    
    // IPFS CID validation - only if not uploading a new file
    if (!eventFile && !isValidIpfsCid(eventForm.ipfs_cid)) {
      setFormError('Invalid IPFS CID format. Must start with Qm or bafy');
      return;
    }
    
    setFormError(''); // Clear any previous form errors
    
    try {
      // Get the selected batch details
      const batch = batches.find(b => b.id === eventForm.batch_id);
      if (!batch) {
        setError('Please select a valid batch');
        return;
      }
      
      // If we have a file to upload, upload it first to get the IPFS CID
      let ipfsCid = eventForm.ipfs_cid;
      if (eventFile) {
        ipfsCid = await uploadEventDocument(eventForm.batch_id);
        if (!ipfsCid) {
          setFormError('Failed to upload document to IPFS. Please try again or provide a valid IPFS CID.');
          return; // Prevent form submission if upload fails
        }
      }
      
      // Submit event to the API
      const response = await fetch(`${import.meta.env.VITE_API_URL}/trace/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          batch_id: eventForm.batch_id,
          event_type: eventForm.event_type,
          location: eventForm.location,
          operator: eventForm.operator,
          temperature: eventForm.temperature ? parseFloat(eventForm.temperature) : null,
          humidity: eventForm.humidity ? parseFloat(eventForm.humidity) : null,
          notes: eventForm.notes,
          ipfs_cid: ipfsCid,
          // Use current time if not specified
          timestamp: new Date().toISOString()
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to add event');
      }
      
      // Reset form
      setEventForm({
        batch_id: '',
        event_type: '',
        location: '',
        temperature: '',
        humidity: '',
        operator: '',
        notes: '',
        ipfs_cid: '',
      });
      
      // Reset file input
      setEventFile(null);
      // Reset file input element if it exists
      const fileInput = document.querySelector('input[type="file"]');
      if (fileInput) {
        fileInput.value = '';
      }
      setShowEventForm(false);
      
      // Refresh the batch events if we were looking at this batch
      if (selectedBatch === eventForm.batch_id) {
        viewBatchEvents(eventForm.batch_id);
      }
      
      // Also refresh the batches to get updated status
      fetchTraceabilityData();
      
    } catch (err) {
      console.error('Error adding traceability event:', err);
      setError(err.message || 'Failed to add event');
      
      // If we fail, still close the form but show an error
      setShowEventForm(false);
    }
  };
  
  const viewBatchEvents = async (batchId) => {
    setSelectedBatch(batchId);
    
    try {
      // Fetch events for this batch from the API
      const eventsResponse = await fetch(`${import.meta.env.VITE_API_URL}/trace/list/${batchId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!eventsResponse.ok) {
        const errorData = await eventsResponse.json();
        throw new Error(errorData.detail || 'Failed to fetch events');
      }
      
      const eventsData = await eventsResponse.json();
      
      // If no events are found, display an appropriate message
      if (eventsData.length === 0) {
        setError('No events recorded for this batch yet');
      } else {
        setError('');
      }
      
      setEvents(eventsData);
    } catch (err) {
      console.error('Error fetching batch events:', err);
      
      // Fallback to mock data for the selected batch if API call fails
      const mockEvents = [
        { id: 'trace_mock1', batch_id: batchId, batch_number: batches.find(b => b.id === batchId)?.batch_number || 'Unknown', event_type: 'production', timestamp: '2025-05-01T08:30:00', location: 'Factory A', temperature: 22, humidity: 45, operator: 'John Smith', notes: 'Initial production run', blockchain_tx_hash: '0x1a2b3c...' },
        { id: 'trace_mock2', batch_id: batchId, batch_number: batches.find(b => b.id === batchId)?.batch_number || 'Unknown', event_type: 'quality_check', timestamp: '2025-05-01T14:15:00', location: 'Factory A QC Lab', temperature: 21, humidity: 43, operator: 'Jane Doe', notes: 'All tests passed', blockchain_tx_hash: '0x4d5e6f...' }
      ];
      
      setEvents(mockEvents);
      setError('Failed to load event data from server. Displaying mock events.');
    }
  };
  
  const getEventTypeColor = (type) => {
    switch(type) {
      case 'production':
        return darkMode ? 'bg-green-700 text-green-100' : 'bg-green-100 text-green-800';
      case 'quality_check':
        return darkMode ? 'bg-blue-700 text-blue-100' : 'bg-blue-100 text-blue-800';
      case 'packaging':
        return darkMode ? 'bg-purple-700 text-purple-100' : 'bg-purple-100 text-purple-800';
      case 'shipping':
        return darkMode ? 'bg-yellow-700 text-yellow-100' : 'bg-yellow-100 text-yellow-800';
      case 'receiving':
        return darkMode ? 'bg-indigo-700 text-indigo-100' : 'bg-indigo-100 text-indigo-800';
      case 'storage':
        return darkMode ? 'bg-gray-700 text-gray-100' : 'bg-gray-100 text-gray-800';
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
          <h1 className="text-3xl font-bold">Traceability</h1>
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
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel: Batch List */}
          <div className={`rounded-lg shadow-md p-6 ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">Product Batches</h2>
              <div className="flex items-center">
                <button
                  onClick={() => {
                    setSelectedBatch(null);
                    setShowEventForm(!showEventForm);
                  }}
                  className={`text-sm px-3 py-1 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200`}
                >
                  {showEventForm ? 'Cancel' : 'Add Event'}
                </button>
              </div>
            </div>
            
            <div className="space-y-4">
              {batches.map((batch) => (
                <div
                  key={batch.id}
                  onClick={() => viewBatchEvents(batch.id)}
                  className={`p-4 rounded-md cursor-pointer transition duration-200 ${
                    selectedBatch === batch.id
                      ? darkMode ? 'bg-blue-900 border-l-4 border-blue-500' : 'bg-blue-50 border-l-4 border-blue-500'
                      : darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-50 hover:bg-gray-100'
                  }`}
                >
                  <h3 className="font-medium">{batch.product_name}</h3>
                  <div className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Batch: {batch.batch_number}
                  </div>
                  <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                    Production: {batch.production_date}
                  </div>
                </div>
              ))}
              
              {batches.length === 0 && (
                <div className={`text-center p-4 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  No batches available for tracking
                </div>
              )}
            </div>
          </div>
          
          {/* Middle/Right Panel: Events Timeline or Event Form */}
          <div className={`lg:col-span-2 rounded-lg shadow-md p-6 ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
            {showEventForm ? (
              <>
                <h2 className="text-xl font-semibold mb-6">Record Tracking Event</h2>
                <form onSubmit={handleEventSubmit}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Select Batch
                      </label>
                      <select
                        name="batch_id"
                        value={eventForm.batch_id}
                        onChange={handleEventFormChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                        required
                      >
                        <option value="">Select Batch</option>
                        {batches.map(batch => (
                          <option key={batch.id} value={batch.id}>
                            {batch.product_name} - {batch.batch_number}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Event Type
                      </label>
                      <select
                        name="event_type"
                        value={eventForm.event_type}
                        onChange={handleEventFormChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                        required
                      >
                        <option value="">Select Event Type</option>
                        <option value="production">Production</option>
                        <option value="quality_check">Quality Check</option>
                        <option value="packaging">Packaging</option>
                        <option value="shipping">Shipping</option>
                        <option value="receiving">Receiving</option>
                        <option value="storage">Storage</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                    <div>
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Location
                      </label>
                      <input
                        type="text"
                        name="location"
                        value={eventForm.location}
                        onChange={handleEventFormChange}
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
                        Operator
                      </label>
                      <input
                        type="text"
                        name="operator"
                        value={eventForm.operator}
                        onChange={handleEventFormChange}
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
                        Temperature (°C)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        name="temperature"
                        value={eventForm.temperature}
                        onChange={handleEventFormChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                      />
                    </div>
                    <div>
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Humidity (%)
                      </label>
                      <input
                        type="number"
                        step="0.1"
                        name="humidity"
                        value={eventForm.humidity}
                        onChange={handleEventFormChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Notes
                      </label>
                      <textarea
                        name="notes"
                        rows="3"
                        value={eventForm.notes}
                        onChange={handleEventFormChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                      ></textarea>
                    </div>
                    <div className="md:col-span-2">
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Document Upload <span className="text-red-500">*</span>
                      </label>
                      <div className={`flex items-center w-full px-3 py-2 border rounded-md ${
                        darkMode 
                          ? 'bg-gray-700 border-gray-600 text-white' 
                          : 'bg-white border-gray-300 text-gray-900'
                      }`}>
                        <input
                          type="file"
                          onChange={handleFileChange}
                          className="text-sm cursor-pointer"
                          required={!eventForm.ipfs_cid}
                        />
                      </div>
                      <p className={`mt-1 text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        Upload a document to be stored on IPFS (required unless you provide an IPFS CID below)
                      </p>
                    </div>
                    <div className="md:col-span-2">
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        IPFS CID <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        name="ipfs_cid"
                        value={eventForm.ipfs_cid}
                        onChange={handleEventFormChange}
                        placeholder="IPFS Content ID if you've already uploaded documents"
                        className={`w-full px-3 py-2 border rounded-md ${
                          !eventFile && !eventForm.ipfs_cid ? 'border-red-500' :
                          !eventFile && !isValidIpfsCid(eventForm.ipfs_cid) ? 'border-yellow-500' :
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                        required={!eventFile}
                      />
                      <p className={`mt-1 text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        Required - Either upload a file above or provide an IPFS CID here (must start with Qm or bafy)
                      </p>
                    </div>
                  </div>
                  {formError && (
                    <div className="mt-4 p-3 bg-red-100 border-l-4 border-red-500 text-red-700 rounded-md">
                      {formError}
                    </div>
                  )}
                  {formError && (
                    <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                      <p>{formError}</p>
                    </div>
                  )}
                  <div className="mt-6">
                    <button
                      type="submit"
                      className={`px-5 py-2 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200`}
                    >
                      Record Event
                    </button>
                  </div>
                </form>
              </>
            ) : selectedBatch ? (
              <>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold">Event Timeline</h2>
                  <span className="text-sm px-3 py-1 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                    {batches.find(b => b.id === selectedBatch)?.batch_number || 'Unknown Batch'}
                  </span>
                </div>
                
                <div className="relative">
                  {/* Timeline line */}
                  <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-300 dark:bg-gray-600"></div>
                  
                  {/* Events */}
                  <div className="space-y-8">
                    {events
                      .filter(event => event.batch_id === selectedBatch)
                      .sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp))
                      .map((event, index) => (
                        <div key={event.id} className="relative pl-10">
                          {/* Timeline dot */}
                          <div className={`absolute left-0 top-2 h-10 w-10 flex items-center justify-center rounded-full border-4 ${
                            darkMode ? 'border-gray-700 bg-gray-800' : 'border-white bg-gray-50'
                          }`}>
                            <span className="text-lg">
                              {event.event_type === 'production' && '🏭'}
                              {event.event_type === 'quality_check' && '✅'}
                              {event.event_type === 'packaging' && '📦'}
                              {event.event_type === 'shipping' && '🚚'}
                              {event.event_type === 'receiving' && '📥'}
                              {event.event_type === 'storage' && '🏪'}
                              {!['production', 'quality_check', 'packaging', 'shipping', 'receiving', 'storage'].includes(event.event_type) && '🔄'}
                            </span>
                          </div>
                          
                          <div className={`p-4 rounded-md ${darkMode ? 'bg-gray-700' : 'bg-white'} shadow-md`}>
                            <div className="flex justify-between items-center mb-2">
                              <span className={`px-2 text-xs font-medium rounded-full ${getEventTypeColor(event.event_type)}`}>
                                {event.event_type.replace('_', ' ')}
                              </span>
                              <span className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                                {new Date(event.timestamp).toLocaleString()}
                              </span>
                            </div>
                            
                            <h3 className="font-medium mb-2">
                              {event.location}
                            </h3>
                            
                            <div className="grid grid-cols-2 gap-2 mb-3 text-sm">
                              <div>
                                <span className={`${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Operator: </span>
                                {event.operator}
                              </div>
                              <div>
                                <span className={`${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Conditions: </span>
                                {event.temperature !== undefined && event.temperature !== '' ? `${event.temperature}°C` : ''}
                                {event.temperature !== undefined && event.temperature !== '' && event.humidity !== undefined && event.humidity !== '' ? ', ' : ''}
                                {event.humidity !== undefined && event.humidity !== '' ? `${event.humidity}% RH` : ''}
                                {!(event.temperature || event.humidity) && 'Not recorded'}
                              </div>
                            </div>
                            
                            {event.notes && (
                              <p className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'} mb-3`}>
                                {event.notes}
                              </p>
                            )}
                            
                            <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'} flex items-center`}>
                              <svg className="h-4 w-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M4.083 9h1.946c.089-1.546.383-2.97.837-4.118A6.004 6.004 0 004.083 9zM10 2a8 8 0 100 16 8 8 0 000-16zm0 2c-.076 0-.232.032-.465.262-.238.234-.497.623-.737 1.182-.389.907-.673 2.142-.766 3.556h3.936c-.093-1.414-.377-2.649-.766-3.556-.24-.56-.5-.948-.737-1.182C10.232 4.032 10.076 4 10 4zm3.971 5c-.089-1.546-.383-2.97-.837-4.118A6.004 6.004 0 0115.917 9h-1.946zm-2.003 2H8.032c.093 1.414.377 2.649.766 3.556.24.56.5.948.737 1.182.233.23.389.262.465.262.076 0 .232-.032.465-.262.238-.234.498-.623.737-1.182.389-.907.673-2.142.766-3.556zm1.166 4.118c.454-1.147.748-2.572.837-4.118h1.946a6.004 6.004 0 01-2.783 4.118zm-6.268 0C6.412 13.97 6.118 12.546 6.03 11H4.083a6.004 6.004 0 002.783 4.118z" clipRule="evenodd" />
                              </svg>
                              <span>Blockchain Verified: </span>
                              <a 
                                href="#" 
                                className={`ml-1 underline ${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-800'}`}
                                onClick={(e) => {
                                  e.preventDefault();
                                  alert(`This would link to blockchain explorer for transaction: ${event.blockchain_tx_hash || event.tx_hash}`);
                                }}
                              >
                                {event.blockchain_tx_hash || event.tx_hash || 'Not verified yet'}
                              </a>
                            </div>
                          </div>
                        </div>
                      ))}
                      
                    {events.filter(event => event.batch_id === selectedBatch).length === 0 && (
                      <div className={`text-center p-4 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        No events recorded for this batch
                      </div>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center h-full py-16">
                <div className={`text-6xl mb-4 ${darkMode ? 'text-gray-600' : 'text-gray-300'}`}>🔍</div>
                <h3 className="text-xl font-semibold mb-2">Select a Batch</h3>
                <p className={`text-center ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  Select a batch from the list to view its tracking events timeline
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Traceability;
