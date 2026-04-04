import httpx
import asyncio

async def test_upload():
    print("Testing upload to http://127.0.0.1:3001/api/upload...")
    files = {'file': ('test_upload.txt', open('test_upload.txt', 'rb'), 'text/plain')}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://127.0.0.1:3001/api/upload", files=files, timeout=30.0)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_upload())
