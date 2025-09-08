const { test, expect } = require('@playwright/test');

test.describe('TherapyBot Chat Tests', () => {
  
  test.beforeEach(async ({ page }) => {
    // Mock API responses
    await page.route('**/messages/chat', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user_message: 'Hello',
          ai_response: 'Hello! I\'m here to help you today. How are you feeling?'
        })
      });
    });
    
    await page.route('**/messages/voice-chat', async route => {
      const requestBody = await route.request().postDataJSON();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          user_message: requestBody.message || 'I need help with anxiety',
          ai_response: 'I understand you need help. Can you tell me more about what you\'re experiencing?'
        })
      });
    });
    
    // Mock auth
    await page.addInitScript(() => {
      localStorage.setItem('token', 'mock-token');
    });
    
    await page.goto('http://localhost:3000/chat');
  });

  test('should send text message and receive AI response', async ({ page }) => {
    // Type message
    await page.fill('input[placeholder*="Type your message"]', 'Hello, I need help');
    
    // Send message
    await page.click('button:has-text("Send")');
    
    // Wait for AI response
    await expect(page.locator('.message.ai').last()).toContainText('Hello! I\'m here to help');
    
    // Verify user message appears
    await expect(page.locator('.message.user').last()).toContainText('Hello, I need help');
  });

  test('should handle voice input', async ({ page }) => {
    // Mock speech recognition
    await page.addInitScript(() => {
      window.SpeechRecognition = class MockSpeechRecognition {
        constructor() {
          this.continuous = false;
          this.interimResults = true;
          this.lang = 'en-US';
        }
        
        start() {
          setTimeout(() => {
            if (this.onstart) this.onstart();
            setTimeout(() => {
              if (this.onresult) {
                this.onresult({
                  resultIndex: 0,
                  results: [{
                    0: { transcript: 'I need help with anxiety' },
                    isFinal: true
                  }]
                });
              }
              if (this.onend) this.onend();
            }, 100);
          }, 50);
        }
        
        stop() {
          if (this.onend) this.onend();
        }
      };
    });
    
    // Click voice button
    await page.click('button[title*="Start Voice Input"]');
    
    // Wait for recording to start and finish
    await page.waitForTimeout(200);
    
    // Verify AI response appears (flexible matching)
    await expect(page.locator('.message.ai').last()).toContainText(/I understand you need help/i, { timeout: 10000 });
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/messages/chat', async route => {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({
          error: 'AI service unavailable'
        })
      });
    });
    
    // Send message
    await page.fill('input[placeholder*="Type your message"]', 'Test message');
    await page.click('button:has-text("Send")');
    
    // Verify error message appears
    await expect(page.locator('.message.ai').last()).toContainText('trouble connecting');
  });

  test('should show voice not supported message', async ({ page }) => {
    // Mock no speech recognition support
    await page.addInitScript(() => {
      delete window.SpeechRecognition;
      delete window.webkitSpeechRecognition;
    });
    
    await page.reload();
    
    // Verify voice not supported message
    await expect(page.locator('text=Voice input not supported')).toBeVisible();
    
    // Verify voice button is disabled
    await expect(page.locator('button[title*="Voice input not supported"]')).toBeDisabled();
  });

  test('should display connection status', async ({ page }) => {
    // Verify status is shown
    await expect(page.locator('text=Status: Connected')).toBeVisible();
    
    // Verify privacy message
    await expect(page.locator('text=Your conversation is private')).toBeVisible();
  });
});