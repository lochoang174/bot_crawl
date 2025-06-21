"""
Example usage of URL Repository
"""

from services.database import init_database, close_database
from repositories.url_repository import UrlRepository


def main():
    """Example usage of URL repository"""
    print("🔗 URL Repository Example Usage")
    print("=" * 40)
    
    # Initialize database connection
    if not init_database():
        print("❌ Failed to connect to MongoDB")
        return
    
    try:
        repo = UrlRepository()
        
        # Example 1: Create URLs
        print("\n1️⃣ Creating URLs...")
        urls = [
            ("https://linkedin.com/in/johndoe", "pending", 1),
            ("https://linkedin.com/in/janedoe", "new", 2),
            ("https://linkedin.com/in/bobsmith", "processing", 3)
        ]
        
        created_ids = []
        for url, status, vm in urls:
            url_id = repo.create(url, status, vm)
            created_ids.append(url_id)
            print(f"   ✅ Created: {url} (ID: {url_id})")
        
        # Example 2: Get URL by ID
        print(f"\n2️⃣ Getting URL by ID: {created_ids[0]}")
        url_obj = repo.get_by_id(created_ids[0])
        if url_obj:
            print(f"   📄 URL: {url_obj.url}")
            print(f"   📊 Status: {url_obj.status}")
            print(f"   🖥️ VM: {url_obj.vm}")
            print(f"   📅 Created: {url_obj.createAt}")
        
        # Example 3: Update status
        print(f"\n3️⃣ Updating status for ID: {created_ids[1]}")
        repo.update_status(created_ids[1], "done")
        updated_obj = repo.get_by_id(created_ids[1])
        print(f"   ✅ Status updated to: {updated_obj.status}")
        
        # Example 4: Find by status
        print("\n4️⃣ Finding URLs by status...")
        pending_urls = repo.find_by_status("pending")
        new_urls = repo.find_by_status("new")
        done_urls = repo.find_by_status("done")
        
        print(f"   📋 Pending: {len(pending_urls)} URLs")
        print(f"   📋 New: {len(new_urls)} URLs")
        print(f"   📋 Done: {len(done_urls)} URLs")
        
        # Example 5: Delete a URL
        print(f"\n5️⃣ Deleting URL: {created_ids[2]}")
        repo.delete(created_ids[2])
        deleted_obj = repo.get_by_id(created_ids[2])
        if deleted_obj is None:
            print("   ✅ URL deleted successfully")
        else:
            print("   ❌ Failed to delete URL")
        
        print("\n🎉 Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        close_database()
        print("\n🔌 Database connection closed")


if __name__ == "__main__":
    main() 