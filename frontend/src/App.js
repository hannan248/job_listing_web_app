import React, { useState, useEffect } from 'react';
import { jobsAPI } from './api';
import AddEditJob from './components/AddEditJob';
import { SimpleDeleteJob } from './components/DeleteJob';
import FilterSortJob from './components/FilterSortJob';
import './App.css';

function App() {
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentView, setCurrentView] = useState('list'); // 'list', 'add', 'edit'
  const [selectedJob, setSelectedJob] = useState(null);
  const [filters, setFilters] = useState({});
  const [apiStatus, setApiStatus] = useState('checking');

  // Check API health and load jobs on mount
  useEffect(() => {
    checkAPIHealth();
    loadJobs();
  }, []);

  // Load jobs when filters change
  useEffect(() => {
    loadJobs(filters);
  }, [filters]);

  const checkAPIHealth = async () => {
    try {
      await jobsAPI.healthCheck();
      setApiStatus('connected');
    } catch (error) {
      setApiStatus('disconnected');
      console.error('API health check failed:', error);
    }
  };

  const loadJobs = async (currentFilters = {}) => {
    setIsLoading(true);
    setError('');

    try {
      const response = await jobsAPI.getJobs(currentFilters);
      setJobs(response.data || []);
    } catch (error) {
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFiltersChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleJobSaved = (savedJob) => {
    if (currentView === 'add') {
      // Add new job to list
      setJobs(prev => [savedJob, ...prev]);
    } else if (currentView === 'edit') {
      // Update existing job in list
      setJobs(prev => prev.map(job => 
        job.id === savedJob.id ? savedJob : job
      ));
    }
    
    setCurrentView('list');
    setSelectedJob(null);
  };

  const handleJobDeleted = (deletedJobId) => {
    setJobs(prev => prev.filter(job => job.id !== deletedJobId));
  };

  const handleEditJob = (job) => {
    setSelectedJob(job);
    setCurrentView('edit');
  };

  const handleCancelEdit = () => {
    setCurrentView('list');
    setSelectedJob(null);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      return 'N/A';
    }
  };

  const renderJobCard = (job) => (
    <div key={job.id} className="job-card">
      <div className="job-header">
        <h3 className="job-title">{job.title}</h3>
        <div className="job-actions">
          <button
            onClick={() => handleEditJob(job)}
            className="btn btn-primary btn-sm"
          >
            Edit
          </button>
          <SimpleDeleteJob
            job={job}
            onDelete={handleJobDeleted}
          />
        </div>
      </div>
      
      <div className="job-details">
        <p className="company">{job.company}</p>
        <p className="location">{job.location}</p>
        <p className="job-type">{job.job_type}</p>
        <p className="posting-date">Posted: {formatDate(job.posting_date)}</p>
        
        {job.tags && job.tags.length > 0 && (
          <div className="job-tags">
            {job.tags.map((tag, index) => (
              <span key={index} className="tag">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const renderJobList = () => (
    <div className="jobs-section">
      <div className="jobs-header">
        <h2>Job Listings ({jobs.length})</h2>
        <button
          onClick={() => setCurrentView('add')}
          className="btn btn-primary"
        >
          Add New Job
        </button>
      </div>

      <FilterSortJob onFiltersChange={handleFiltersChange} />

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="loading">
          Loading jobs...
        </div>
      )}

      {!isLoading && jobs.length === 0 && !error && (
        <div className="no-jobs">
          <p>No jobs found.</p>
          <button
            onClick={() => setCurrentView('add')}
            className="btn btn-primary"
          >
            Add the first job
          </button>
        </div>
      )}

      {!isLoading && jobs.length > 0 && (
        <div className="jobs-grid">
          {jobs.map(renderJobCard)}
        </div>
      )}
    </div>
  );

  return (
    <div className="App">
      <header className="app-header">
        <div className="header-content">
          <h1>Job Listing Portal</h1>
          <div className="header-info">
            <div className={`api-status ${apiStatus}`}>
              API: {apiStatus === 'connected' ? 'Connected' : 'Disconnected'}
            </div>
            {currentView !== 'list' && (
              <button
                onClick={handleCancelEdit}
                className="btn btn-secondary"
              >
                Back to Jobs
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {currentView === 'list' && renderJobList()}
          
          {currentView === 'add' && (
            <AddEditJob
              onSave={handleJobSaved}
              onCancel={handleCancelEdit}
              isEditing={false}
            />
          )}
          
          {currentView === 'edit' && selectedJob && (
            <AddEditJob
              job={selectedJob}
              onSave={handleJobSaved}
              onCancel={handleCancelEdit}
              isEditing={true}
            />
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>&copy; 2024 Job Listing Portal. Built with React and Flask.</p>
      </footer>
    </div>
  );
}

export default App;