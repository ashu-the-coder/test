import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../App';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';

function EnterpriseProfile() {
  const { token } = useContext(AuthContext);
  const { darkMode } = useTheme();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    company_name: '',
    business_email: '',
    industry: '',
    employee_count: '',
    contact_person: '',
    contact_phone: ''
  });

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchProfile = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/profile`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to load enterprise profile');
        }

        const data = await response.json();
        setProfile(data);
        setFormData({
          company_name: data.company_name || '',
          business_email: data.business_email || '',
          industry: data.industry || '',
          employee_count: data.employee_count || '',
          contact_person: data.contact_person || '',
          contact_phone: data.contact_phone || ''
        });
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchProfile();
  }, [token, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: name === 'employee_count' ? parseInt(value) || '' : value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/enterprise/update`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update profile');
      }

      // Update was successful
      const updatedProfile = await response.json();
      setProfile(updatedProfile);
      setEditMode(false);
    } catch (err) {
      setError(err.message);
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
      <div className="max-w-4xl mx-auto">
        <div className="mb-10 flex justify-between items-center">
          <h1 className="text-3xl font-bold">Enterprise Profile</h1>
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

        <div className={`rounded-lg shadow-md p-6 ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
          {!editMode ? (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className={`text-lg font-semibold mb-1 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>Company Information</h3>
                  <div className="space-y-3">
                    <div>
                      <span className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Company Name</span>
                      <span className="block font-medium">{profile?.company_name || 'N/A'}</span>
                    </div>
                    <div>
                      <span className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Business Email</span>
                      <span className="block font-medium">{profile?.business_email || 'N/A'}</span>
                    </div>
                    <div>
                      <span className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Industry</span>
                      <span className="block font-medium">{profile?.industry || 'N/A'}</span>
                    </div>
                    <div>
                      <span className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Employee Count</span>
                      <span className="block font-medium">{profile?.employee_count || 'N/A'}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className={`text-lg font-semibold mb-1 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>Contact Information</h3>
                  <div className="space-y-3">
                    <div>
                      <span className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Contact Person</span>
                      <span className="block font-medium">{profile?.contact_person || 'N/A'}</span>
                    </div>
                    <div>
                      <span className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Contact Phone</span>
                      <span className="block font-medium">{profile?.contact_phone || 'N/A'}</span>
                    </div>
                    <div>
                      <span className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Username</span>
                      <span className="block font-medium">{profile?.username || 'N/A'}</span>
                    </div>
                    <div>
                      <span className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Wallet Address</span>
                      <span className="block font-medium text-xs break-all">{profile?.wallet_address || 'Not connected'}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-8">
                <button
                  onClick={() => setEditMode(true)}
                  className={`px-5 py-2 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200`}
                >
                  Edit Profile
                </button>
              </div>
            </>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className={`text-lg font-semibold mb-3 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>Company Information</h3>
                  <div className="space-y-4">
                    <div>
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Company Name
                      </label>
                      <input
                        type="text"
                        name="company_name"
                        value={formData.company_name}
                        onChange={handleChange}
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
                        Business Email
                      </label>
                      <input
                        type="email"
                        name="business_email"
                        value={formData.business_email}
                        onChange={handleChange}
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
                        Industry
                      </label>
                      <select
                        name="industry"
                        value={formData.industry}
                        onChange={handleChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                        required
                      >
                        <option value="">Select Industry</option>
                        <option value="technology">Technology</option>
                        <option value="healthcare">Healthcare</option>
                        <option value="finance">Finance</option>
                        <option value="education">Education</option>
                        <option value="manufacturing">Manufacturing</option>
                        <option value="retail">Retail</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                    <div>
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Employee Count
                      </label>
                      <input
                        type="number"
                        name="employee_count"
                        value={formData.employee_count}
                        onChange={handleChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                        required
                      />
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className={`text-lg font-semibold mb-3 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`}>Contact Information</h3>
                  <div className="space-y-4">
                    <div>
                      <label className={`block text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'} mb-1`}>
                        Contact Person
                      </label>
                      <input
                        type="text"
                        name="contact_person"
                        value={formData.contact_person}
                        onChange={handleChange}
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
                        Contact Phone
                      </label>
                      <input
                        type="tel"
                        name="contact_phone"
                        value={formData.contact_phone}
                        onChange={handleChange}
                        className={`w-full px-3 py-2 border rounded-md ${
                          darkMode 
                            ? 'bg-gray-700 border-gray-600 text-white' 
                            : 'bg-white border-gray-300 text-gray-900'
                        } focus:outline-none focus:ring-2 focus:ring-blue-500`}
                      />
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="mt-8 flex gap-4">
                <button
                  type="submit"
                  className={`px-5 py-2 rounded-md ${darkMode ? 'bg-blue-600 hover:bg-blue-700' : 'bg-blue-500 hover:bg-blue-600'} text-white transition duration-200`}
                >
                  Save Changes
                </button>
                <button
                  type="button"
                  onClick={() => setEditMode(false)}
                  className={`px-5 py-2 rounded-md ${
                    darkMode 
                      ? 'bg-gray-700 hover:bg-gray-600' 
                      : 'bg-gray-200 hover:bg-gray-300'
                  } transition duration-200`}
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

export default EnterpriseProfile;
