// Example of how to call /api/auth/me from frontend
async function getUserProfile() {
  // Get token from localStorage or wherever you store it
  const token = localStorage.getItem('access_token');
  
  try {
    const response = await fetch('http://your-api-url/api/auth/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      // Handle error responses
      if (response.status === 401) {
        console.error('Unauthorized: Please log in again');
        // Redirect to login page or refresh token
      } else {
        console.error(`Error: ${response.status}`);
      }
      return null;
    }
    
    // Parse and return user data
    const userData = await response.json();
    return userData;
  } catch (error) {
    console.error('Failed to fetch user profile:', error);
    return null;
  }
}

// Usage
getUserProfile().then(user => {
  if (user) {
    console.log('User profile:', user);
    // Update UI with user information
  }
});