import json

def handler(request):
    """Vercel serverless function handler"""
    try:
        # Parse request
        if request.method == 'POST':
            # Read request body
            body = request.body.decode('utf-8')
            request_data = json.loads(body)
            
            # Create a simple response for now
            response_data = {
                "status": "success",
                "message": "API endpoint working!",
                "received": {
                    "repoUrl": request_data.get('repoUrl'),
                    "prompt": request_data.get('prompt')
                }
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps(response_data)
            }
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({"error": "Method not allowed"})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        } 