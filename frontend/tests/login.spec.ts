import { test, expect } from '@playwright/test';

/**
 * Test Suite: User Authentication and Navigation
 * This test suite verifies the login functionality and subsequent navigation behaviors.
 */

const credentials = {
    username: "", 
    password: ""
}

test.describe('User Authentication', () => {
  
  test('should successfully log in and display user-specific actions', async ({ page }) => {
    // Navigate to the login page
    await page.goto('/login/');

    // Fill in & submit the login credentials
    await page.fill('input[name="username"]', credentials.username);
    await page.fill('input[name="password"]', credentials.password);
    await page.click('button:has-text("Login")');

    // Verify navigation to the user profile page
    await page.waitForURL('/profile/');

    // Validate the visibility of the "Upload Bot" button on the profile page
    const uploadBotButton = await page.locator('button:has-text("Upload Bot")');
    await expect(uploadBotButton).toBeVisible();
  });

  test('should redirect to profile after login and allow re-accessing /login', async ({ page }) => {
    // Step 1: Perform login and verify navigation to profile
    await page.goto('/login/');

    // Fill in the login credentials
    await page.fill('input[name="username"]', credentials.username);
    await page.fill('input[name="password"]', credentials.password);

    // Submit the login form
    await page.click('button:has-text("Login")');
    await page.waitForURL('/profile/');

    // Step 2: Attempt to navigate back to the login page
    await page.goto('/login/');

    // Verify that the user is redirected back to the profile page
    await page.waitForURL('/profile/');

    // Validate the visibility of the "Upload Bot" button again
    const uploadBotButton = await page.locator('button:has-text("Upload Bot")');
    await expect(uploadBotButton).toBeVisible();
  });

});