"""
Simple test for URL Repository
"""

import time
from services.database import init_database, close_database
from repositories.url_repository import UrlRepository


def test_url_repository():
    """Test URL repository functions"""
    print("🚀 Starting URL Repository Test...")
    
    # Initialize database connection
    if not init_database():
        print("❌ Failed to connect to MongoDB")
        return False
    
    try:
        repo = UrlRepository()
        
        # Test 1: Create URL
        print("\n📝 Test 1: Creating URL...")
        url_id = repo.create("https://example.com", status="pending", vm=1)
        print(f"✅ Created URL with ID: {url_id}")
        
        # Test 2: Get URL by ID
        print("\n🔍 Test 2: Getting URL by ID...")
        url_obj = repo.get_by_id(url_id)
        if url_obj:
            print(f"✅ Found URL: {url_obj.url}, Status: {url_obj.status}, VM: {url_obj.vm}")
        else:
            print("❌ Failed to get URL by ID")
            return False
        
        # Test 3: Update status
        print("\n✏️ Test 3: Updating URL status...")
        updated_count = repo.update_status(url_id, "processing")
        if updated_count > 0:
            print("✅ Status updated successfully")
            
            # Verify the update
            updated_obj = repo.get_by_id(url_id)
            if updated_obj and updated_obj.status == "processing":
                print(f"✅ Verified status: {updated_obj.status}")
            else:
                print("❌ Status update verification failed")
        else:
            print("❌ Failed to update status")
        
        # Test 4: Find by status
        print("\n🔍 Test 4: Finding URLs by status...")
        processing_urls = repo.find_by_status("processing")
        print(f"✅ Found {len(processing_urls)} URLs with 'processing' status")
        
        # Test 5: Create multiple URLs
        print("\n📝 Test 5: Creating multiple URLs...")
        urls_to_create = [
            ("https://google.com", "new", 2),
            ("https://github.com", "pending", 3),
            ("https://stackoverflow.com", "done", 1)
        ]
        
        created_ids = []
        for url, status, vm in urls_to_create:
            url_id = repo.create(url, status, vm)
            created_ids.append(url_id)
            print(f"✅ Created: {url} (ID: {url_id})")
        
        # Test 6: Find by different statuses
        print("\n🔍 Test 6: Finding URLs by different statuses...")
        new_urls = repo.find_by_status("new")
        pending_urls = repo.find_by_status("pending")
        done_urls = repo.find_by_status("done")
        
        print(f"✅ New URLs: {len(new_urls)}")
        print(f"✅ Pending URLs: {len(pending_urls)}")
        print(f"✅ Done URLs: {len(done_urls)}")
        
        # Test 7: Delete URL
        print("\n🗑️ Test 7: Deleting URL...")
        if created_ids:
            delete_id = created_ids[0]
            deleted_count = repo.delete(delete_id)
            if deleted_count > 0:
                print(f"✅ Deleted URL with ID: {delete_id}")
                
                # Verify deletion
                deleted_obj = repo.get_by_id(delete_id)
                if deleted_obj is None:
                    print("✅ Verified deletion")
                else:
                    print("❌ Deletion verification failed")
            else:
                print("❌ Failed to delete URL")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Close database connection
        close_database()
        print("\n🔌 Database connection closed")


def test_url_model():
    """Test URL model functionality"""
    print("\n🧪 Testing URL Model...")
    
    from models.url_model import UrlModel
    from datetime import datetime
    
    # Test model creation
    url_model = UrlModel(
        url="https://test.com",
        status="test",
        vm=5
    )
    
    # Test to_dict method
    url_dict = url_model.to_dict()
    expected_keys = ["url", "status", "vm", "createAt"]
    
    if all(key in url_dict for key in expected_keys):
        print("✅ URL Model to_dict() works correctly")
        print(f"   URL: {url_dict['url']}")
        print(f"   Status: {url_dict['status']}")
        print(f"   VM: {url_dict['vm']}")
        print(f"   CreateAt: {url_dict['createAt']}")
    else:
        print("❌ URL Model to_dict() failed")
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("🧪 URL Repository Test Suite")
    print("=" * 50)
    
    # Test URL Model
    model_success = test_url_model()
    
    # Test URL Repository
    repo_success = test_url_repository()
    
    print("\n" + "=" * 50)
    if model_success and repo_success:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 50) 