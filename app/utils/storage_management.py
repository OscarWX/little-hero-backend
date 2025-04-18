import argparse
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so that app modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Load environment variables
load_dotenv()

from app.utils.storage import (
    s3_client, 
    delete_file_from_s3, 
    delete_files_from_s3, 
    configure_lifecycle_policy
)

async def list_objects(prefix=None):
    """List objects in the S3 bucket."""
    bucket_name = os.getenv("S3_BUCKET_NAME")
    kwargs = {'Bucket': bucket_name}
    if prefix:
        kwargs['Prefix'] = prefix
    
    try:
        response = s3_client.list_objects_v2(**kwargs)
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"{obj['Key']} - {obj['Size']} bytes - {obj['LastModified']}")
        else:
            print(f"No objects found in bucket {bucket_name} with prefix {prefix}")
    except Exception as e:
        print(f"Error listing objects: {str(e)}")

async def delete_object(key):
    """Delete an object from the S3 bucket."""
    try:
        result = delete_file_from_s3(key)
        print(f"Successfully deleted {key}" if result else f"Failed to delete {key}")
    except Exception as e:
        print(f"Error deleting object: {str(e)}")

async def delete_objects_with_prefix(prefix):
    """Delete all objects with a specific prefix from the S3 bucket."""
    bucket_name = os.getenv("S3_BUCKET_NAME")
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        if 'Contents' in response:
            keys = [obj['Key'] for obj in response['Contents']]
            result = delete_files_from_s3(keys)
            print(f"Successfully deleted {len(keys)} objects with prefix {prefix}" if result 
                  else f"Failed to delete objects with prefix {prefix}")
        else:
            print(f"No objects found with prefix {prefix}")
    except Exception as e:
        print(f"Error deleting objects: {str(e)}")

async def setup_lifecycle():
    """Configure lifecycle policy for the S3 bucket."""
    result = configure_lifecycle_policy()
    print("Lifecycle policy configured successfully" if result else "Failed to configure lifecycle policy")

async def main():
    parser = argparse.ArgumentParser(description="Manage S3 storage for Little Hero")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List objects command
    list_parser = subparsers.add_parser("list", help="List objects in the S3 bucket")
    list_parser.add_argument("--prefix", help="Prefix to filter objects")
    
    # Delete object command
    delete_parser = subparsers.add_parser("delete", help="Delete an object from the S3 bucket")
    delete_parser.add_argument("key", help="The key of the object to delete")
    
    # Delete objects with prefix command
    delete_prefix_parser = subparsers.add_parser("delete-prefix", help="Delete all objects with a prefix")
    delete_prefix_parser.add_argument("prefix", help="The prefix of the objects to delete")
    
    # Setup lifecycle command
    subparsers.add_parser("setup-lifecycle", help="Configure lifecycle policy for the S3 bucket")
    
    args = parser.parse_args()
    
    if args.command == "list":
        await list_objects(args.prefix)
    elif args.command == "delete":
        await delete_object(args.key)
    elif args.command == "delete-prefix":
        await delete_objects_with_prefix(args.prefix)
    elif args.command == "setup-lifecycle":
        await setup_lifecycle()
    else:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main()) 