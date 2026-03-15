# MCP Server — Gemini Subagent for Geoglypha
# Ryan Lafferty
#
# Exposes Gemini and GCS as tools available to Claude Code.
# Tools: gemini_query, gcs_read, gcs_write, gcs_list

import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.cloud import storage
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "www.geoglypha1.org")

app = Server("gemini-geoglypha")


@app.list_tools()
async def list_tools():
	return [
		types.Tool(
			name="gemini_query",
			description=(
				"Send a prompt to Gemini 1.5 Pro with optional context. "
				"Use for content generation, analysis, editing suggestions, "
				"or summarizing data from other projects."
			),
			inputSchema={
				"type": "object",
				"properties": {
					"prompt": {
						"type": "string",
						"description": "The instruction or question for Gemini"
					},
					"context": {
						"type": "string",
						"description": "Optional content to pass as context (file text, data, etc.)"
					}
				},
				"required": ["prompt"]
			}
		),
		types.Tool(
			name="gcs_read",
			description="Read a text file from the Geoglypha GCS bucket (www.geoglypha1.org).",
			inputSchema={
				"type": "object",
				"properties": {
					"path": {
						"type": "string",
						"description": "File path within the bucket, e.g. index.html or graphita/graphitia.html"
					}
				},
				"required": ["path"]
			}
		),
		types.Tool(
			name="gcs_write",
			description="Upload/overwrite a file in the Geoglypha GCS bucket (www.geoglypha1.org).",
			inputSchema={
				"type": "object",
				"properties": {
					"path": {
						"type": "string",
						"description": "Destination path in the bucket, e.g. index.html"
					},
					"content": {
						"type": "string",
						"description": "Full file content to upload"
					},
					"content_type": {
						"type": "string",
						"description": "MIME type, defaults to text/html",
						"default": "text/html"
					}
				},
				"required": ["path", "content"]
			}
		),
		types.Tool(
			name="gcs_list",
			description="List files in the Geoglypha GCS bucket. Optionally filter by path prefix.",
			inputSchema={
				"type": "object",
				"properties": {
					"prefix": {
						"type": "string",
						"description": "Optional prefix to filter results, e.g. graphita/"
					}
				}
			}
		),
	]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
	if name == "gemini_query":
		model = genai.GenerativeModel("gemini-1.5-pro")
		prompt = arguments["prompt"]
		context = arguments.get("context", "")
		full_prompt = f"{context}\n\n{prompt}" if context else prompt
		response = model.generate_content(full_prompt)
		return [types.TextContent(type="text", text=response.text)]

	elif name == "gcs_read":
		client = storage.Client()
		bucket = client.bucket(BUCKET_NAME)
		blob = bucket.blob(arguments["path"])
		content = blob.download_as_text()
		return [types.TextContent(type="text", text=content)]

	elif name == "gcs_write":
		client = storage.Client()
		bucket = client.bucket(BUCKET_NAME)
		blob = bucket.blob(arguments["path"])
		content_type = arguments.get("content_type", "text/html")
		blob.upload_from_string(arguments["content"], content_type=content_type)
		return [types.TextContent(
			type="text",
			text=f"Uploaded {arguments['path']} to {BUCKET_NAME}"
		)]

	elif name == "gcs_list":
		client = storage.Client()
		bucket = client.bucket(BUCKET_NAME)
		prefix = arguments.get("prefix", "")
		blobs = list(bucket.list_blobs(prefix=prefix))
		file_list = "\n".join(b.name for b in blobs)
		return [types.TextContent(type="text", text=file_list or "No files found.")]

	raise ValueError(f"Unknown tool: {name}")


async def main():
	async with stdio_server() as (read_stream, write_stream):
		await app.run(
			read_stream,
			write_stream,
			app.create_initialization_options()
		)


if __name__ == "__main__":
	asyncio.run(main())
