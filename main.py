import requests
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pdf_manager import PdfManager
from openai_client import OpenAiClient
from vector_manager import VectorManager
from agents import tables_extraction_agent, text_extraction_agent
from schemas import TablesSchema, ExtractedTextSchema
from chunkify_data import chunkify

app = FastAPI()

@app.post("/api/preprocess")
async def preprocess_file(file_url: str = Query(...)):

    client = OpenAiClient()
    pdf_manager = PdfManager()
    vector_manager = VectorManager()
    try:
        # Send GET request to fetch the file
        response = requests.get(file_url, stream=True)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)

        # File content in memory
        file_content = response.content
        content_type = response.headers.get("Content-Type")  # e.g., application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document

        # Map MIME type to file type
        mime_to_type = {
            "application/pdf": "pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        }

        file_type = mime_to_type.get(content_type)
        if not file_type:
            raise ValueError(f"Unsupported file type: {content_type}")
     
        extracted_file = pdf_manager.pdf_reader(file_content, file_type)

        # Extract tables and text
        extracted_tables = pdf_manager.extract(client, extracted_file, TablesSchema, tables_extraction_agent)
        extracted_text = pdf_manager.extract(client, extracted_file, ExtractedTextSchema, text_extraction_agent)

        # Chunkify the text
        chunkified_text = chunkify(extracted_text.text)

        # Return success response with preprocessing result
        return JSONResponse(
            status_code=200,
            content={
                "message": "File processed successfully",
                "file_url": file_url
            }
        )
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Failed to fetch file: {str(e)}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"An error occurred: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
