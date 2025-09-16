import sys
from pymongo import MongoClient

# Set console to use UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

# MongoDB connection details
MONGO_URI = "mongodb+srv://a99andres56_db_user:hlxIJzLKwPtEWayO@breadbot.aqvugjd.mongodb.net/?retryWrites=true&w=majority&appName=breadbot"

try:
    # Connect to MongoDB with SSL settings
    print("Connecting to MongoDB...")
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsAllowInvalidCertificates=False,
        tlsAllowInvalidHostnames=True,
        retryWrites=True,
        w='majority',
        appName='breadbot'
    )
    
    # Test the connection
    client.admin.command('ping')
    print("[SUCCESS] Connected to MongoDB!")
    
    # Access the database and collection
    db = client["breadbot"]
    config_collection = db["config"]
    
    # Count documents in the collection
    count = config_collection.count_documents({})
    print(f"\nFound {count} document(s) in the config collection")
    
    # Print all documents
    if count > 0:
        print("\n=== Channel Configurations ===")
        for doc in config_collection.find():
            print("\nDocument ID:", doc.get("_id"))
            print("Guild ID:", doc.get("guild_id"))
            print("Log Channel ID:", doc.get("log_channel", "Not set"))
            print("Welcome Channel ID:", doc.get("welcome_channel", "Not set"))
    else:
        print("No channel configurations found in the database.")
    
    print("\n=== End of Data ===")
    
except Exception as e:
    print(f"[ERROR] {e}")
    
finally:
    # Close the connection
    if 'client' in locals():
        client.close()
        print("\nMongoDB connection closed.")
