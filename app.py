from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import uvicorn
import os
from supabase import create_client, Client

# Initialize FastAPI app
app = FastAPI(
    title="Simple Data API with Supabase",
    description="A simple API to receive and post data to both memory and Supabase",
    version="1.0.0"
)

# Supabase configuration
SUPABASE_URL = "https://gbkhkbfbarsnpbdkxzii.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdia2hrYmZiYXJzbnBiZGt4emlpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzQzODAzNzMsImV4cCI6MjA0OTk1NjM3M30.mcOcC2GVEu_wD3xNBzSCC3MwDck3CIdmz4D8adU-bpI"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# In-memory storage (for backward compatibility)
data_store = []

# Pydantic models for request/response
class DataItem(BaseModel):
    id: Optional[int] = None
    name: str
    value: Any
    description: Optional[str] = None

class DataResponse(BaseModel):
    message: str
    data: Optional[DataItem] = None
    total_items: Optional[int] = None

# Helper function to store data in Supabase
async def store_in_supabase(data_item: dict):
    """Store data in Supabase micropy table, test column"""
    try:
        # Prepare data for Supabase
        supabase_data = {
            "test": {
                "id": data_item.get("id"),
                "name": data_item.get("name"),
                "value": data_item.get("value"),
                "description": data_item.get("description"),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Insert into Supabase
        result = supabase.table("micropy").insert(supabase_data).execute()
        return result
    except Exception as e:
        print(f"Error storing in Supabase: {e}")
        return None

# Helper function to get data from Supabase
async def get_from_supabase():
    """Retrieve data from Supabase micropy table"""
    try:
        result = supabase.table("micropy").select("*").execute()
        return result.data
    except Exception as e:
        print(f"Error retrieving from Supabase: {e}")
        return []

# Root endpoint
@app.get("/")
async def root():
    return {"message": "FastAPI Data Service with Supabase is running!", "status": "healthy"}

# Test page with HTML form (same as before but with Supabase info)
@app.get("/test1")
async def test_page():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI Data Test with Supabase</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .form-group { margin: 15px 0; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
            button:hover { background: #0056b3; }
            .response { margin-top: 20px; padding: 15px; border-radius: 4px; }
            .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
            .data-list { background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 4px; }
            .data-item { margin: 10px 0; padding: 10px; background: white; border: 1px solid #dee2e6; border-radius: 3px; }
            .supabase-info { background: #e3f2fd; border: 1px solid #bbdefb; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>🧪 FastAPI Data Test Page with Supabase</h1>
        <div class="supabase-info">
            <p><strong>🗄️ Database:</strong> Data is now stored in both memory and Supabase database</p>
            <p><strong>📊 Table:</strong> micropy → test column</p>
        </div>
        
        <h2>📝 Create New Data</h2>
        <form id="dataForm">
            <div class="form-group">
                <label>Name:</label>
                <input type="text" id="name" name="name" required placeholder="Enter item name">
            </div>
            <div class="form-group">
                <label>Value:</label>
                <input type="text" id="value" name="value" required placeholder="Enter any value">
            </div>
            <div class="form-group">
                <label>Description:</label>
                <textarea id="description" name="description" rows="3" placeholder="Optional description"></textarea>
            </div>
            <button type="submit">📤 POST Data (Memory + Supabase)</button>
            <button type="button" onclick="loadData()">🔄 Load Memory Data</button>
            <button type="button" onclick="loadSupabaseData()">📊 Load Supabase Data</button>
            <button type="button" onclick="clearData()">🗑️ Clear Display</button>
        </form>
        
        <div id="response"></div>
        
        <h2>📊 Memory Data</h2>
        <div id="dataList"></div>
        
        <h2>🗄️ Supabase Data</h2>
        <div id="supabaseDataList"></div>
        
        <p>
            <a href="/test1/mydata" target="_blank">📋 View memory data</a> |
            <a href="/supabase-data" target="_blank">🗄️ View Supabase data</a>
        </p>
        
        <script>
            // POST form data
            document.getElementById('dataForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = {
                    name: document.getElementById('name').value,
                    value: document.getElementById('value').value,
                    description: document.getElementById('description').value || null
                };
                
                try {
                    const response = await fetch('/data', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('response').innerHTML = 
                            '<div class="response success"><strong>✅ Success!</strong><br>' +
                            'Message: ' + result.message + '<br>' +
                            'Created ID: ' + result.data.id + '<br>' +
                            'Total Items: ' + result.total_items + '<br>' +
                            '<strong>📊 Stored in both memory and Supabase!</strong></div>';
                        
                        // Clear form
                        document.getElementById('dataForm').reset();
                        
                        // Auto-load both data sources
                        loadData();
                        loadSupabaseData();
                    } else {
                        throw new Error(result.detail || 'Unknown error');
                    }
                    
                } catch (error) {
                    document.getElementById('response').innerHTML = 
                        '<div class="response error"><strong>❌ Error!</strong><br>' + error.message + '</div>';
                }
            });
            
            // Load memory data
            async function loadData() {
                try {
                    const response = await fetch('/data');
                    const data = await response.json();
                    
                    let html = '<div class="data-list">';
                    
                    if (data.length === 0) {
                        html += '<p><em>No data stored in memory yet.</em></p>';
                    } else {
                        html += '<p><strong>Total Items in Memory: ' + data.length + '</strong></p>';
                        data.forEach(item => {
                            html += '<div class="data-item">' +
                                '<strong>ID ' + item.id + ':</strong> ' + item.name + '<br>' +
                                '<strong>Value:</strong> ' + JSON.stringify(item.value) + '<br>' +
                                (item.description ? '<strong>Description:</strong> ' + item.description : '') +
                                '</div>';
                        });
                    }
                    
                    html += '</div>';
                    document.getElementById('dataList').innerHTML = html;
                    
                } catch (error) {
                    document.getElementById('dataList').innerHTML = 
                        '<div class="response error">Error loading memory data: ' + error.message + '</div>';
                }
            }
            
            // Load Supabase data
            async function loadSupabaseData() {
                try {
                    const response = await fetch('/supabase-data');
                    const data = await response.json();
                    
                    let html = '<div class="data-list">';
                    
                    if (data.length === 0) {
                        html += '<p><em>No data stored in Supabase yet.</em></p>';
                    } else {
                        html += '<p><strong>Total Items in Supabase: ' + data.length + '</strong></p>';
                        data.forEach(item => {
                            const testData = item.test || {};
                            html += '<div class="data-item">' +
                                '<strong>ID ' + (testData.id || 'N/A') + ':</strong> ' + (testData.name || 'Unnamed') + '<br>' +
                                '<strong>Value:</strong> ' + JSON.stringify(testData.value) + '<br>' +
                                (testData.description ? '<strong>Description:</strong> ' + testData.description + '<br>' : '') +
                                '<small>Timestamp: ' + (testData.timestamp || 'N/A') + '</small>' +
                                '</div>';
                        });
                    }
                    
                    html += '</div>';
                    document.getElementById('supabaseDataList').innerHTML = html;
                    
                } catch (error) {
                    document.getElementById('supabaseDataList').innerHTML = 
                        '<div class="response error">Error loading Supabase data: ' + error.message + '</div>';
                }
            }
            
            // Clear display
            function clearData() {
                document.getElementById('response').innerHTML = '';
                document.getElementById('dataList').innerHTML = '';
                document.getElementById('supabaseDataList').innerHTML = '';
            }
            
            // Load data on page load
            loadData();
            loadSupabaseData();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Simple data view page (updated for memory data)
@app.get("/test1/mydata")
async def my_data_page():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Memory Data - FastAPI</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; background: #f5f5f5; }}
            .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .data-container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .data-item {{ margin: 15px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #007bff; border-radius: 4px; }}
            .data-item h3 {{ margin: 0 0 10px 0; color: #007bff; }}
            .data-value {{ background: #e9ecef; padding: 10px; border-radius: 4px; font-family: monospace; word-break: break-all; }}
            .no-data {{ text-align: center; color: #6c757d; padding: 40px; }}
            .stats {{ background: #e3f2fd; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
            .nav-links {{ margin-top: 20px; }}
            .nav-links a {{ color: #007bff; text-decoration: none; margin-right: 20px; }}
            .nav-links a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 My Memory Data Store</h1>
            <p>All data currently stored in memory (not Supabase)</p>
        </div>
        
        <div class="data-container">
            <div class="stats">
                <strong>📈 Total Items:</strong> <span id="totalCount">Loading...</span> | 
                <strong>🕒 Last Updated:</strong> <span id="lastUpdated">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            
            <div id="dataContent">
                <p style="text-align: center; color: #6c757d;">Loading data...</p>
            </div>
        </div>
        
        <div class="nav-links">
            <a href="/test1">← Back to Test Form</a>
            <a href="/data">📄 Raw JSON Data</a>
            <a href="/supabase-data">🗄️ Supabase Data</a>
            <a href="/health">❤️ Health Check</a>
            <a href="javascript:location.reload()">🔄 Refresh</a>
        </div>
        
        <script>
            async function loadMyData() {{
                try {{
                    const response = await fetch('/data');
                    const data = await response.json();
                    
                    document.getElementById('totalCount').textContent = data.length;
                    
                    let html = '';
                    
                    if (data.length === 0) {{
                        html = '<div class="no-data"><h3>📭 No Data Found</h3><p>Go to <a href="/test1">the test form</a> to add some data!</p></div>';
                    }} else {{
                        data.forEach((item, index) => {{
                            html += `
                                <div class="data-item">
                                    <h3>Item #${{item.id || index + 1}}: ${{item.name || 'Unnamed'}}</h3>
                                    <p><strong>Value:</strong></p>
                                    <div class="data-value">${{JSON.stringify(item.value, null, 2)}}</div>
                                    ${{item.description ? '<p><strong>Description:</strong> ' + item.description + '</p>' : ''}}
                                    <small style="color: #6c757d;">ID: ${{item.id}}</small>
                                </div>
                            `;
                        }});
                    }}
                    
                    document.getElementById('dataContent').innerHTML = html;
                    
                }} catch (error) {{
                    document.getElementById('dataContent').innerHTML = 
                        '<div style="color: #dc3545; text-align: center; padding: 20px;"><strong>❌ Error loading data:</strong><br>' + error.message + '</div>';
                    document.getElementById('totalCount').textContent = 'Error';
                }}
            }}
            
            // Load data on page load
            loadMyData();
            
            // Auto-refresh every 30 seconds
            setInterval(loadMyData, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# NEW: Supabase data view page
@app.get("/supabase-data")
async def supabase_data_page():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Supabase Data - FastAPI</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 50px auto; padding: 20px; background: #f5f5f5; }}
            .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .data-container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .data-item {{ margin: 15px 0; padding: 15px; background: #f0f8ff; border-left: 4px solid #28a745; border-radius: 4px; }}
            .data-item h3 {{ margin: 0 0 10px 0; color: #28a745; }}
            .data-value {{ background: #e9ecef; padding: 10px; border-radius: 4px; font-family: monospace; word-break: break-all; }}
            .no-data {{ text-align: center; color: #6c757d; padding: 40px; }}
            .stats {{ background: #d4edda; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
            .nav-links {{ margin-top: 20px; }}
            .nav-links a {{ color: #007bff; text-decoration: none; margin-right: 20px; }}
            .nav-links a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🗄️ Supabase Data Store</h1>
            <p>All data currently stored in Supabase database (micropy table, test column)</p>
        </div>
        
        <div class="data-container">
            <div class="stats">
                <strong>📈 Total Items:</strong> <span id="totalCount">Loading...</span> | 
                <strong>🕒 Last Updated:</strong> <span id="lastUpdated">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
            </div>
            
            <div id="dataContent">
                <p style="text-align: center; color: #6c757d;">Loading data...</p>
            </div>
        </div>
        
        <div class="nav-links">
            <a href="/test1">← Back to Test Form</a>
            <a href="/test1/mydata">📊 Memory Data</a>
            <a href="/data">📄 Raw JSON Memory Data</a>
            <a href="/health">❤️ Health Check</a>
            <a href="javascript:location.reload()">🔄 Refresh</a>
        </div>
        
        <script>
            async function loadSupabaseData() {{
                try {{
                    const response = await fetch('/supabase-data');
                    const data = await response.json();
                    
                    document.getElementById('totalCount').textContent = data.length;
                    
                    let html = '';
                    
                    if (data.length === 0) {{
                        html = '<div class="no-data"><h3>📭 No Data Found in Supabase</h3><p>Go to <a href="/test1">the test form</a> to add some data!</p></div>';
                    }} else {{
                        data.forEach((item, index) => {{
                            const testData = item.test || {{}};
                            html += `
                                <div class="data-item">
                                    <h3>Supabase Item #${{testData.id || index + 1}}: ${{testData.name || 'Unnamed'}}</h3>
                                    <p><strong>Value:</strong></p>
                                    <div class="data-value">${{JSON.stringify(testData.value, null, 2)}}</div>
                                    ${{testData.description ? '<p><strong>Description:</strong> ' + testData.description + '</p>' : ''}}
                                    <small style="color: #6c757d;">
                                        ID: ${{testData.id}} | 
                                        Timestamp: ${{testData.timestamp || 'N/A'}} |
                                        Supabase ID: ${{item.id || 'N/A'}}
                                    </small>
                                </div>
                            `;
                        }});
                    }}
                    
                    document.getElementById('dataContent').innerHTML = html;
                    
                }} catch (error) {{
                    document.getElementById('dataContent').innerHTML = 
                        '<div style="color: #dc3545; text-align: center; padding: 20px;"><strong>❌ Error loading Supabase data:</strong><br>' + error.message + '</div>';
                    document.getElementById('totalCount').textContent = 'Error';
                }}
            }}
            
            // Load data on page load
            loadSupabaseData();
            
            // Auto-refresh every 30 seconds
            setInterval(loadSupabaseData, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# POST data directly from URL path (updated to store in Supabase too)
@app.get("/test1/{data_value}")
async def post_data_from_url(data_value: str):
    # Create data item from URL parameter
    new_item = {
        "id": len(data_store) + 1,
        "name": f"URL Data #{len(data_store) + 1}",
        "value": data_value,
        "description": f"Data sent via URL at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    }
    
    # Store in memory
    data_store.append(new_item)
    
    # Store in Supabase
    supabase_result = await store_in_supabase(new_item)
    
    # Return success message as HTML
    html_response = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Received - FastAPI with Supabase</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 100px auto; padding: 20px; text-align: center; }}
            .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .data-display {{ background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: left; }}
            .nav-links a {{ color: #007bff; text-decoration: none; margin: 0 10px; }}
            .nav-links a:hover {{ text-decoration: underline; }}
            .supabase-status {{ background: #e3f2fd; border: 1px solid #bbdefb; padding: 10px; border-radius: 4px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>✅ Data Received Successfully!</h1>
        
        <div class="success">
            <h3>Your data has been stored in both memory and Supabase!</h3>
            <p><strong>Data received:</strong> "{data_value}"</p>
            <p><strong>Assigned ID:</strong> {new_item['id']}</p>
            <p><strong>Total items in memory:</strong> {len(data_store)}</p>
        </div>
        
        <div class="supabase-status">
            <strong>🗄️ Supabase Status:</strong> {'✅ Successfully stored' if supabase_result else '❌ Error storing (check logs)'}
        </div>
        
        <div class="data-display">
            <h4>📋 Stored Item Details:</h4>
            <p><strong>ID:</strong> {new_item['id']}</p>
            <p><strong>Name:</strong> {new_item['name']}</p>
            <p><strong>Value:</strong> {new_item['value']}</p>
            <p><strong>Description:</strong> {new_item['description']}</p>
        </div>
        
        <div class="nav-links">
            <a href="/test1/mydata">📊 View Memory Data</a>
            <a href="/supabase-data">🗄️ View Supabase Data</a>
            <a href="/test1">🧪 Test Form</a>
            <a href="/">🏠 Home</a>
        </div>
        
        <hr style="margin: 30px 0;">
        <h3>🚀 Try More Examples:</h3>
        <p>Send data directly in the URL:</p>
        <ul style="text-align: left; display: inline-block;">
            <li><a href="/test1/hello_world">test1/hello_world</a></li>
            <li><a href="/test1/12345">test1/12345</a></li>
            <li><a href="/test1/test_data_123">test1/test_data_123</a></li>
        </ul>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_response)

# Health check endpoint
@app.get("/health")
async def health_check():
    # Test Supabase connection
    try:
        supabase_data = await get_from_supabase()
        supabase_status = "connected"
        supabase_count = len(supabase_data)
    except:
        supabase_status = "error"
        supabase_count = 0
    
    return {
        "status": "healthy", 
        "memory_items": len(data_store),
        "supabase_status": supabase_status,
        "supabase_items": supabase_count
    }

# GET all memory data
@app.get("/data", response_model=List[DataItem])
async def get_all_data():
    return data_store

# NEW: GET all Supabase data
@app.get("/supabase-data")
async def get_supabase_data():
    return await get_from_supabase()

# GET data by ID from memory
@app.get("/data/{item_id}", response_model=DataItem)
async def get_data_by_id(item_id: int):
    for item in data_store:
        if item.get("id") == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

# POST new data (updated to store in both places)
@app.post("/data", response_model=DataResponse)
async def create_data(item: DataItem):
    # Auto-generate ID if not provided
    if item.id is None:
        item.id = len(data_store) + 1
    
    # Convert to dict and store in memory
    item_dict = item.dict()
    data_store.append(item_dict)
    
    # Store in Supabase
    await store_in_supabase(item_dict)
    
    return DataResponse(
        message="Data created successfully in memory and Supabase",
        data=item,
        total_items=len(data_store)
    )

# PUT update data (memory only for now)
@app.put("/data/{item_id}", response_model=DataResponse)
async def update_data(item_id: int, item: DataItem):
    for i, stored_item in enumerate(data_store):
        if stored_item.get("id") == item_id:
            item.id = item_id  # Ensure ID matches
            updated_item = item.dict()
            data_store[i] = updated_item
            
            # Also update in Supabase (store as new entry for simplicity)
            await store_in_supabase(updated_item)
            
            return DataResponse(
                message="Data updated successfully in memory and stored in Supabase",
                data=item,
                total_items=len(data_store)
            )
    raise HTTPException(status_code=404, detail="Item not found")

# DELETE data (memory only for now)
@app.delete("/data/{item_id}", response_model=DataResponse)
async def delete_data(item_id: int):
    for i, item in enumerate(data_store):
        if item.get("id") == item_id:
            deleted_item = data_store.pop(i)
            return DataResponse(
                message="Data deleted successfully from memory (Supabase data remains)",
                data=DataItem(**deleted_item),
                total_items=len(data_store)
            )
    raise HTTPException(status_code=404, detail="Item not found")

# Bulk POST endpoint (updated to store in Supabase)
@app.post("/data/bulk", response_model=DataResponse)
async def create_bulk_data(items: List[DataItem]):
    created_items = []
    for item in items:
        if item.id is None:
            item.id = len(data_store) + 1
        item_dict = item.dict()
        data_store.append(item_dict)
        created_items.append(item)
        
        # Store each item in Supabase
        await store_in_supabase(item_dict)
    
    return DataResponse(
        message=f"Created {len(created_items)} items successfully in memory and Supabase",
        total_items=len(data_store)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)