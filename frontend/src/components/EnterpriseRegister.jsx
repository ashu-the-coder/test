import { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../App';
import { useTheme } from '../contexts/ThemeContext';

function EnterpriseRegister() {
  const [registrationType, setRegistrationType] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleTypeSelection = (type) => {
    if (type === 'individual') {
      // Navigate to the standard register page for individuals
      navigate('/register');
    } else {
      // Set the type to enterprise and show the enterprise form
      setRegistrationType('enterprise');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-200">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
            Choose Registration Type
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            Select the type of account you want to create
          </p>
        </div>

        {!registrationType ? (
          <div className="mt-8 space-y-4">
            <button
              onClick={() => handleTypeSelection('individual')}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 dark:bg-indigo-500 hover:bg-indigo-700 dark:hover:bg-indigo-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 transition-colors duration-200"
            >
              Individual Registration
              <div className="ml-2 text-xs text-indigo-200">For personal use</div>
            </button>
            <button
              onClick={() => handleTypeSelection('enterprise')}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors duration-200"
            >
              Enterprise Registration
              <div className="ml-2 text-xs text-blue-200">For business use</div>
            </button>
          </div>
        ) : (
          <EnterpriseForm />
        )}
        
        <div className="text-center mt-4">
          <Link
            to="/enterprise"
            className="font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300"
          >
            Back to Enterprise Portal
          </Link>
        </div>
      </div>
    </div>
  );
}

function EnterpriseForm() {
  const [formData, setFormData] = useState({
    companyName: '',
    businessEmail: '',
    password: '',
    confirmPassword: '',
    industry: '',
    employeeCount: '',
    contactPerson: '',
    contactPhone: ''
  });
  const [error, setError] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const { darkMode } = useTheme();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Basic validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }

    try {
      // Register enterprise user using the auth/enterprise/register endpoint
      const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/enterprise/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_name: formData.companyName,
          business_email: formData.businessEmail,
          password: formData.password,
          industry: formData.industry,
          employee_count: parseInt(formData.employeeCount) || 0,
          contact_person: formData.contactPerson,
          contact_phone: formData.contactPhone,
          user_type: 'enterprise'
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Enterprise registration failed');
      }

      // After enterprise user registration, also create an enterprise record
      // First log in with the credentials
      login(data.access_token);
      
      // Then create the enterprise record
      const enterpriseResponse = await fetch(`${import.meta.env.VITE_API_URL}/enterprise/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${data.access_token}`
        },
        body: JSON.stringify({
          enterprise_name: formData.companyName,
          industry: formData.industry,
          admin_details: {
            name: formData.contactPerson,
            email: formData.businessEmail,
            phone: formData.contactPhone,
            role: 'admin'
          },
          description: `Enterprise with ${formData.employeeCount} employees`,
        }),
      });

      if (enterpriseResponse.ok) {
        const enterpriseData = await enterpriseResponse.json();
        localStorage.setItem('enterpriseId', enterpriseData.enterprise_id);
        navigate('/enterprise/modules');
      } else {
        // If enterprise record creation fails, continue anyway
        // The user will need to create the enterprise record later
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
      <div className="rounded-md shadow-sm -space-y-px">
        <div>
          <label htmlFor="companyName" className="sr-only">Company Name</label>
          <input
            id="companyName"
            name="companyName"
            type="text"
            required
            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-t-md focus:outline-none focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:z-10 sm:text-sm transition-colors duration-200"
            placeholder="Company Name"
            value={formData.companyName}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="businessEmail" className="sr-only">Business Email</label>
          <input
            id="businessEmail"
            name="businessEmail"
            type="email"
            required
            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 focus:outline-none focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:z-10 sm:text-sm transition-colors duration-200"
            placeholder="Business Email"
            value={formData.businessEmail}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="industry" className="sr-only">Industry</label>
          <select
            id="industry"
            name="industry"
            required
            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 focus:outline-none focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:z-10 sm:text-sm transition-colors duration-200"
            value={formData.industry}
            onChange={handleChange}
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
          <label htmlFor="employeeCount" className="sr-only">Number of Employees</label>
          <input
            id="employeeCount"
            name="employeeCount"
            type="number"
            required
            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 focus:outline-none focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:z-10 sm:text-sm transition-colors duration-200"
            placeholder="Number of Employees"
            value={formData.employeeCount}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="contactPerson" className="sr-only">Contact Person</label>
          <input
            id="contactPerson"
            name="contactPerson"
            type="text"
            required
            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 focus:outline-none focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:z-10 sm:text-sm transition-colors duration-200"
            placeholder="Contact Person Name"
            value={formData.contactPerson}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="contactPhone" className="sr-only">Contact Phone</label>
          <input
            id="contactPhone"
            name="contactPhone"
            type="tel"
            required
            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 focus:outline-none focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:z-10 sm:text-sm transition-colors duration-200"
            placeholder="Contact Phone"
            value={formData.contactPhone}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="password" className="sr-only">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            required
            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 focus:outline-none focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:z-10 sm:text-sm transition-colors duration-200"
            placeholder="Password"
            value={formData.password}
            onChange={handleChange}
          />
        </div>
        <div>
          <label htmlFor="confirmPassword" className="sr-only">Confirm Password</label>
          <input
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            required
            className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-b-md focus:outline-none focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:border-indigo-500 dark:focus:border-indigo-400 focus:z-10 sm:text-sm transition-colors duration-200"
            placeholder="Confirm Password"
            value={formData.confirmPassword}
            onChange={handleChange}
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
          Register Enterprise
        </button>
      </div>
    </form>
  );
}

export default EnterpriseRegister;
