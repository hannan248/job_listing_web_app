from db import db
from datetime import datetime

class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    posting_date = db.Column(db.DateTime, default=datetime.utcnow)
    job_type = db.Column(db.String(50), default='Full-time')
    tags = db.Column(db.Text)  
    
    def __repr__(self):
        return f'<Job {self.id}: {self.title} at {self.company}>'
    
    def to_dict(self):
        """Convert job object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'posting_date': self.posting_date.isoformat() if self.posting_date else None,
            'job_type': self.job_type,
            'tags': self.tags.split(',') if self.tags and self.tags.strip() else []
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create job object from dictionary"""
        job = cls(
            title=data.get('title', '').strip(),
            company=data.get('company', '').strip(),
            location=data.get('location', '').strip(),
            job_type=data.get('job_type', 'Full-time'),
            tags=','.join(data.get('tags', [])) if isinstance(data.get('tags'), list) else data.get('tags', '')
        )
        
        # Handle posting_date if provided
        if 'posting_date' in data and data['posting_date']:
            try:
                job.posting_date = datetime.fromisoformat(data['posting_date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                job.posting_date = datetime.utcnow()
        
        return job
    
    def update_from_dict(self, data):
        """Update job object from dictionary"""
        if 'title' in data:
            self.title = data['title'].strip()
        if 'company' in data:
            self.company = data['company'].strip()
        if 'location' in data:
            self.location = data['location'].strip()
        if 'job_type' in data:
            self.job_type = data['job_type']
        if 'tags' in data:
            if isinstance(data['tags'], list):
                self.tags = ','.join(data['tags'])
            else:
                self.tags = data['tags']
        if 'posting_date' in data and data['posting_date']:
            try:
                self.posting_date = datetime.fromisoformat(data['posting_date'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass  