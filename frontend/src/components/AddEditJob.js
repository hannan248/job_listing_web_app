import React, { useState, useEffect } from 'react';
import { jobsAPI } from '../api';

const AddEditJob = ({ job, onSave, onCancel, isEditing = false }) => {
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    location: '',
    job_type: 'Full-time',
    tags: '',
    posting_date: ''
  });
  
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    if (isEditing && job) {
      setFormData({
        title: job.title || '',
        company: job.company || '',
        location: job.location || '',
        job_type: job.job_type || 'Full-time',
        tags: Array.isArray(job.tags) ? job.tags.join(', ') : (job.tags || ''),
        posting_date: job.posting_date ? job.posting_date.split('T')[0] : ''
      });
    }
  }, [job, isEditing]);

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Job title is required';
    }
    
    if (!formData.company.trim()) {
      newErrors.company = 'Company name is required';
    }
    
    if (!formData.location.trim()) {
      newErrors.location = 'Location is required';
    }
    
    if (!['Full-time', 'Part-time', 'Contract', 'Internship'].includes(formData.job_type)) {
      newErrors.job_type = 'Please select a valid job type';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    setErrors({});
    setSuccessMessage('');
    
    try {
      const jobData = {
        ...formData,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      };
      
      let result;
      if (isEditing) {
        result = await jobsAPI.updateJob(job.id, jobData);
      } else {
        result = await jobsAPI.createJob(jobData);
      }
      
      setSuccessMessage(isEditing ? 'Job updated successfully!' : 'Job created successfully!');
      
      if (!isEditing) {
        setFormData({
          title: '',
          company: '',
          location: '',
          job_type: 'Full-time',
          tags: '',
          posting_date: ''
        });
      }
      
      if (onSave) {
        onSave(result.data);
      }
      
    } catch (error) {
      setErrors({ general: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      title: '',
      company: '',
      location: '',
      job_type: 'Full-time',
      tags: '',
      posting_date: ''
    });
    setErrors({});
    setSuccessMessage('');
    
    if (onCancel) {
      onCancel();
    }
  };

  return (
    <div className="add-edit-job">
      <h2>{isEditing ? 'Edit Job' : 'Add New Job'}</h2>
      
      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}
      
      {errors.general && (
        <div className="error-message">
          {errors.general}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="job-form">
        <div className="form-group">
          <label htmlFor="title">Job Title *</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            className={errors.title ? 'error' : ''}
            placeholder="e.g., Senior Actuary - Life Insurance"
          />
          {errors.title && <span className="error-text">{errors.title}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="company">Company Name *</label>
          <input
            type="text"
            id="company"
            name="company"
            value={formData.company}
            onChange={handleInputChange}
            className={errors.company ? 'error' : ''}
            placeholder="e.g., Aon, Milliman, Deloitte"
          />
          {errors.company && <span className="error-text">{errors.company}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="location">Location *</label>
          <input
            type="text"
            id="location"
            name="location"
            value={formData.location}
            onChange={handleInputChange}
            className={errors.location ? 'error' : ''}
            placeholder="e.g., New York, NY or Remote"
          />
          {errors.location && <span className="error-text">{errors.location}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="job_type">Job Type</label>
          <select
            id="job_type"
            name="job_type"
            value={formData.job_type}
            onChange={handleInputChange}
            className={errors.job_type ? 'error' : ''}
          >
            <option value="Full-time">Full-time</option>
            <option value="Part-time">Part-time</option>
            <option value="Contract">Contract</option>
            <option value="Internship">Internship</option>
          </select>
          {errors.job_type && <span className="error-text">{errors.job_type}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="tags">Tags/Skills</label>
          <input
            type="text"
            id="tags"
            name="tags"
            value={formData.tags}
            onChange={handleInputChange}
            placeholder="e.g., Life, Health, Python, Pricing (comma-separated)"
          />
          <small className="help-text">Enter tags separated by commas</small>
        </div>

        <div className="form-group">
          <label htmlFor="posting_date">Posting Date</label>
          <input
            type="date"
            id="posting_date"
            name="posting_date"
            value={formData.posting_date}
            onChange={handleInputChange}
          />
          <small className="help-text">Leave blank to use current date</small>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isLoading}
          >
            {isLoading ? 'Saving...' : (isEditing ? 'Update Job' : 'Add Job')}
          </button>
          
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleCancel}
            disabled={isLoading}
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default AddEditJob;