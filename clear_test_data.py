import sqlite3
import os
import glob

def clear_test_data():
    # 1. Clear database records (keeping users)
    print("Connecting to database...")
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM shared_files")
    # Reset auto-increment counter for shared_files
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='shared_files'")
    
    conn.commit()
    conn.close()
    print("Successfully cleared all messages from database!")

    # 2. Delete test images from uploads folder
    print("Cleaning up old image files...")
    
    original_files = glob.glob('static/uploads/originals/*')
    encrypted_files = glob.glob('static/uploads/encrypted/*')
    
    count = 0
    for f in original_files + encrypted_files:
        try:
            os.remove(f)
            count += 1
        except Exception as e:
            print(f"Failed to delete {f}: {e}")
            
    print(f"Deleted {count} old test files.")
    print("Cleanup complete! You can now start testing freshly.")

if __name__ == '__main__':
    clear_test_data()
