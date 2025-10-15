# Project Blueprint

## Overview

This Flutter application implements a basic login and logout system with a custom dark theme. It uses `provider` for state management, `google_fonts` for typography, and `go_router` for navigation.

## Style and Design

*   **Theme**: Dark theme with primary color #00796B (teal) and secondary color #FFC107 (yellow/orange).
*   **Fonts**: Open Sans from Google Fonts.
*   **Login Screen**:
    *   Header: Placeholder icon with "shop.io" text.
    *   Welcome Message: "Welcome Back" in bold, followed by an instruction message.
    *   Input Fields: Email and Password with borders.
    *   Buttons: "Forgot Password?" text button and a prominent "Sign In" button.
    *   Social Login: "Or sign in with" separator, Google and Apple login buttons.
*   **Home Screen**:
    *   Simple screen with a "Welcome!" message and a logout button.

## Features

*   **Login**: Validates non-empty fields and navigates to the home screen.
*   **Logout**: Navigates back to the login screen.

## Current Changes

*   Implemented the login and logout functionality.
*   Added the home placeholder screen.
*   Added the Google and Apple login buttons (without functionality).

## Next Steps

*   Implement real authentication.
*   Implement the sign-up screen.
*   Connect to a real backend.
