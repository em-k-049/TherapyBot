// Simple test to verify speech recognition support detection
function testSpeechRecognition() {
  console.log('Testing Speech Recognition Support...');
  
  // Check if SpeechRecognition is available
  window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  
  if (window.SpeechRecognition) {
    console.log('✅ Speech Recognition is supported');
    console.log('Browser supports:', window.SpeechRecognition.name);
    return true;
  } else {
    console.log('❌ Speech Recognition is NOT supported');
    console.log('Please use Chrome or Edge for voice features');
    return false;
  }
}

// Test function for browser compatibility
function getBrowserInfo() {
  const userAgent = navigator.userAgent;
  let browserName = 'Unknown';
  
  if (userAgent.includes('Chrome')) browserName = 'Chrome';
  else if (userAgent.includes('Firefox')) browserName = 'Firefox';
  else if (userAgent.includes('Safari')) browserName = 'Safari';
  else if (userAgent.includes('Edge')) browserName = 'Edge';
  
  console.log('Browser:', browserName);
  console.log('User Agent:', userAgent);
  
  return browserName;
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { testSpeechRecognition, getBrowserInfo };
}

// Auto-run test if in browser
if (typeof window !== 'undefined') {
  getBrowserInfo();
  testSpeechRecognition();
}