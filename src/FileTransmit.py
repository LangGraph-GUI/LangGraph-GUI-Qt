# FileTransmit.py

from typing import List
import os
import zipfile
import io
from datetime import datetime
import json

from fastapi import HTTPException, BackgroundTasks
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.responses import StreamingResponse
from fastapi.responses import Response


# Create a router instance
file_router = APIRouter()

# Utility function to get or create a user's workspace directory
def get_or_create_workspace(username: str) -> str:
    """
    Ensures the workspace directory for a given username exists.
    Creates the directory if it doesn't exist.
    """
    workspace_path = os.path.join('./workspace/', username)
    if not os.path.exists(workspace_path):
        os.makedirs(workspace_path)
        print(f"Created workspace for {username} at {workspace_path}")
    return workspace_path


@file_router.get('/download/{username}')
async def download_workspace(username: str):
    try:
        user_workspace = get_or_create_workspace(username)

        # Create a zip file from the user's workspace directory
        zip_filename = f'{username}_workspace.zip'
        zip_buffer = io.BytesIO()  # in-memory buffer to hold the zip file

        # Create a ZipFile object in write mode
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Walk through the workspace directory and add files to the zip
            for root, dirs, files in os.walk(user_workspace):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, user_workspace)  # Store files relative to the workspace
                    zip_file.write(file_path, arcname)

        # Seek to the beginning of the buffer before sending it
        zip_buffer.seek(0)

        # Return the zip file as a Response, without triggering stat checks
        return Response(
            zip_buffer.read(),  # Read the content of the BytesIO object
            media_type="application/zip",  # Set the media type to zip file
            headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
        )
    
    except Exception as e:
        print(f"Error creating zip: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create zip file: {str(e)}")

# Route to handle file uploads with username
@file_router.post('/upload/{username}')
async def upload_file(username: str, files: List[UploadFile] = File(...)):
    user_workspace = get_or_create_workspace(username)

    if not files:
        raise HTTPException(status_code=400, detail="No files selected for uploading")

    # Save each uploaded file to the user's workspace
    for file in files:
        file_path = os.path.join(user_workspace, file.filename)
        with open(file_path, 'wb') as f:
            f.write(await file.read())
        print(f"Uploaded file: {file.filename} to {user_workspace}")
    
    return JSONResponse(content={"message": "Files successfully uploaded"}, status_code=200)

# Route to handle saving graph data as JSON with username
@file_router.post('/save-graph/{username}')
async def save_graph(username: str, graph_data: dict):
    try:
        # Get or create the user's workspace
        user_workspace = get_or_create_workspace(username)

        # Save the JSON data to a file in the user's workspace
        graph_file_path = os.path.join(user_workspace, 'graph.json')
        with open(graph_file_path, 'w') as graph_file:
            json.dump(graph_data, graph_file, indent=2)

        print(f"Graph data saved to {graph_file_path}")
        return JSONResponse(content={"message": "Graph data successfully saved"}, status_code=200)

    except Exception as e:
        print(f"Error saving graph data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save graph data: {str(e)}")

# Route to handle cleaning the user's workspace
@file_router.post('/clean-cache/{username}')
async def clean_cache(username: str):
    try:
        # Get or create the user's workspace
        user_workspace = get_or_create_workspace(username)

        # Delete all files in the user's workspace
        for root, dirs, files in os.walk(user_workspace):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

        return JSONResponse(content={"message": "Workspace successfully cleaned"}, status_code=200)

    except Exception as e:
        print(f"Error cleaning workspace: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clean workspace: {str(e)}")
