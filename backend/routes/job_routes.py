from flask import Blueprint, request, jsonify
from db import db
from models.job import Job
from sqlalchemy import or_

job_routes = Blueprint('jobs', __name__)

# Input validation helper
def validate_job_data(data, required_fields=None):
    if required_fields is None:
        required_fields = ['title', 'company', 'location']
    
    errors = []
    
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            errors.append(f"{field} is required")
    
    if 'job_type' in data and data['job_type'] not in ['Full-time', 'Part-time', 'Contract', 'Internship']:
        errors.append("job_type must be one of: Full-time, Part-time, Contract, Internship")
    
    return errors

@job_routes.route('/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs with optional filtering and sorting"""
    try:
        query = Job.query
        
        # Filtering parameters
        job_type = request.args.get('job_type')
        location = request.args.get('location')
        tag = request.args.get('tag')
        search = request.args.get('search')
        
        # Apply filters
        if job_type:
            query = query.filter(Job.job_type == job_type)
        
        if location:
            query = query.filter(Job.location.ilike(f'%{location}%'))
        
        if tag:
            query = query.filter(Job.tags.ilike(f'%{tag}%'))
        
        if search:
            query = query.filter(
                or_(
                    Job.title.ilike(f'%{search}%'),
                    Job.company.ilike(f'%{search}%')
                )
            )
        
        # Sorting
        sort_by = request.args.get('sort', 'posting_date_desc')
        
        if sort_by == 'posting_date_desc':
            query = query.order_by(Job.posting_date.desc())
        elif sort_by == 'posting_date_asc':
            query = query.order_by(Job.posting_date.asc())
        elif sort_by == 'title_asc':
            query = query.order_by(Job.title.asc())
        elif sort_by == 'company_asc':
            query = query.order_by(Job.company.asc())
        else:
            # Default sort
            query = query.order_by(Job.posting_date.desc())
        
        jobs = query.all()
        
        return jsonify({
            'success': True,
            'data': [job.to_dict() for job in jobs],
            'count': len(jobs)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch jobs',
            'message': str(e)
        }), 500

@job_routes.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Get a single job by ID"""
    try:
        job = Job.query.get(job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': job.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch job',
            'message': str(e)
        }), 500

@job_routes.route('/jobs', methods=['POST'])
def create_job():
    """Create a new job"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate input
        errors = validate_job_data(data)
        if errors:
            return jsonify({
                'success': False,
                'error': 'Validation failed',
                'errors': errors
            }), 400
        
        # Create new job using model method
        job = Job.from_dict(data)
        
        db.session.add(job)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': job.to_dict(),
            'message': 'Job created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to create job',
            'message': str(e)
        }), 500

@job_routes.route('/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    """Update an existing job"""
    try:
        job = Job.query.get(job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate input (only check provided fields)
        provided_fields = [field for field in ['title', 'company', 'location'] if field in data]
        if provided_fields:  # Only validate if there are fields to validate
            errors = validate_job_data(data, provided_fields)
            if errors:
                return jsonify({
                    'success': False,
                    'error': 'Validation failed',
                    'errors': errors
                }), 400
        
        # Update job using model method
        job.update_from_dict(data)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': job.to_dict(),
            'message': 'Job updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to update job',
            'message': str(e)
        }), 500

@job_routes.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job"""
    try:
        job = Job.query.get(job_id)
        
        if not job:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
        
        db.session.delete(job)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Job deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to delete job',
            'message': str(e)
        }), 500

# Health check endpoint
@job_routes.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Job API is running',
        'version': '1.0.0'
    }), 200

@job_routes.route('/jobs/job-types', methods=['GET'])
def get_job_types():
    """Get unique job types"""
    try:
        job_types = db.session.query(Job.job_type).distinct().all()
        job_types = [jt[0] for jt in job_types if jt[0]]
        
        return jsonify({
            'success': True,
            'data': job_types
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch job types',
            'message': str(e)
        }), 500

# Get unique locations for dropdown
@job_routes.route('/jobs/locations', methods=['GET'])
def get_locations():
    """Get unique locations"""
    try:
        locations = db.session.query(Job.location).distinct().all()
        locations = [loc[0] for loc in locations if loc[0]]
        
        return jsonify({
            'success': True,
            'data': locations
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch locations',
            'message': str(e)
        }), 500

# Get all unique tags
@job_routes.route('/jobs/tags', methods=['GET'])
def get_tags():
    """Get all unique tags"""
    try:
        jobs_with_tags = db.session.query(Job.tags).filter(Job.tags.isnot(None)).all()
        all_tags = set()
        
        for job_tags in jobs_with_tags:
            if job_tags[0]:
                tags = [tag.strip() for tag in job_tags[0].split(',') if tag.strip()]
                all_tags.update(tags)
        
        return jsonify({
            'success': True,
            'data': sorted(list(all_tags))
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch tags',
            'message': str(e)
        }), 500