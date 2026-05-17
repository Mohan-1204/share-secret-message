import requests

# Set up session
session = requests.Session()

# The app is running locally on http://127.0.0.1:5000

def test_upload():
    # 1. Register a user (or try logging in, but since we don't know the DB state, we can register)
    res = session.post('http://127.0.0.1:5000/register', data={
        'name': 'Test User',
        'gender': 'Male',
        'email': 'test@example.com',
        'phone': '1234567890',
        'address': 'Test',
        'uname': 'testuser',
        'password': 'password'
    })
    
    # 2. Login
    res = session.post('http://127.0.0.1:5000/login', data={
        'email': 'test@example.com',
        'password': 'password'
    })
    print("Login status:", res.status_code)

    # 3. Try to hit upload page (GET)
    res = session.get('http://127.0.0.1:5000/upload')
    print("GET upload status:", res.status_code)

    # 4. Create a dummy image
    import numpy as np
    import cv2
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite('dummy.png', img)

    # 5. POST to upload
    with open('dummy.png', 'rb') as f:
        files = {'cover_image': ('dummy.png', f, 'image/png')}
        data = {
            'receiver_id': '1', # Doesn't matter if it's correct for now, we just want to see if it 500s
            'secret_text': 'This is a secret'
        }
        res = session.post('http://127.0.0.1:5000/upload', files=files, data=data)
        
    print("POST upload status:", res.status_code)
    if res.status_code == 500:
        print("Got 500 Error!")
        print(res.text)
    else:
        print("Success or redirect!")
        print("Redirect URL:", res.url)

if __name__ == '__main__':
    test_upload()
