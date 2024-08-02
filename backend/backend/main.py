from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import re

app = Flask(__name__)
CORS(app)

# Database to store changes
changes_db = {}
companies = set()

def load_changes():
    global changes_db, companies
    diffs_dir = 'diffs'
    
    for company in os.listdir(diffs_dir):
        companies.add(company)
        company_dir = os.path.join(diffs_dir, company)
        
        for diff_file in os.listdir(company_dir):
            if diff_file.startswith('diff_') and diff_file.endswith('.json'):
                with open(os.path.join(company_dir, diff_file), 'r') as f:
                    diff_data = json.load(f)
                
                # Extract information from filename
                match = re.match(r'diff_(\d{8}_\d{6})_(\d{8}_\d{6})\.json', diff_file)
                if match:
                    from_version, to_version = match.groups()
                    change_id = f"{company}_{from_version}_{to_version}"
                    
                    # Create change object
                    change = {
                        "id": change_id,
                        "company": company,
                        "from_version": f"{from_version}.json",
                        "to_version": f"{to_version}.json",
                        "timestamp": datetime.strptime(to_version, "%Y%m%d_%H%M%S").isoformat() + "Z",
                        "summary": diff_data.get('summary', {}),
                        "diff": diff_data.get('diff', {})
                    }
                    
                    changes_db[change_id] = change

# Load changes when the app starts
load_changes()

@app.route('/api/changes', methods=['GET'])
def get_recent_changes():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 20))
    company = request.args.get('company')
    change_size = request.args.get('changeSize')
    from_date = request.args.get('fromDate')
    to_date = request.args.get('toDate')

    filtered_changes = list(changes_db.values())

    # Apply filters
    if company:
        filtered_changes = [c for c in filtered_changes if c['company'] == company]
    if change_size:
        # Implement change size filtering logic
        size_thresholds = {'small': 10, 'medium': 50, 'large': 100}
        threshold = size_thresholds.get(change_size.lower())
        if threshold:
            filtered_changes = [c for c in filtered_changes if c['summary']['total_changes'] >= threshold]
    if from_date:
        from_dt = datetime.strptime(from_date, "%Y-%m-%d")
        filtered_changes = [c for c in filtered_changes if datetime.fromisoformat(c['timestamp'][:-1]) >= from_dt]
    if to_date:
        to_dt = datetime.strptime(to_date, "%Y-%m-%d")
        filtered_changes = [c for c in filtered_changes if datetime.fromisoformat(c['timestamp'][:-1]) <= to_dt]

    # Sort changes by timestamp (newest first)
    filtered_changes.sort(key=lambda x: x['timestamp'], reverse=True)

    # Paginate
    start = (page - 1) * limit
    end = start + limit
    paginated_changes = filtered_changes[start:end]

    return jsonify({
        "total": len(filtered_changes),
        "page": page,
        "limit": limit,
        "changes": paginated_changes
    })

@app.route('/api/changes/<string:id>', methods=['GET'])
def get_change_details(id):
    change = changes_db.get(id)
    if not change:
        return jsonify({"error": "Change not found"}), 404
    return jsonify(change)

@app.route('/api/companies', methods=['GET'])
def get_companies():
    return jsonify({"companies": list(companies)})

if __name__ == '__main__':
    app.run(debug=True)