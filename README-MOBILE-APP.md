# PLAYAM Mobile App (Staging)

This branch packages the existing PLAYAM staging game as a cross-platform Capacitor app.

## Safety
- The app bundle is configured for the PLAYAM-Staging Supabase project only.
- It retains the visible STAGING ONLY warning.
- Use test accounts only. Do not use production credentials or real player data.
- This branch does not change production code, production database, or production hosting.
- No payment, wallet, withdrawal, or LIVE features are enabled by this app package.

## Android test build
1. Open the repository's **Actions** tab.
2. Select **PLAYAM Android test build**.
3. Choose **Run workflow** on branch `codex/playam-mobile-app`.
4. When it finishes, download the `playam-android-staging-debug` artifact.
5. Extract the ZIP and install `app-debug.apk` on an Android test phone.

This is a private debug build for testing, not a Play Store release.

## iPhone
Capacitor iOS builds require macOS and Xcode. Installing on a physical iPhone or distributing through TestFlight/App Store requires Apple signing and the appropriate Apple Developer account. The source is prepared for iOS, but no signed iPhone IPA has been produced yet.

## Build locally
Requires Node.js 22+, Android Studio/Android SDK for Android, and macOS with Xcode for iOS.

```sh
npm install
npx cap add android
npx cap sync android
npx cap open android
```

For iOS on macOS:

```sh
npx cap add ios
npx cap sync ios
npx cap open ios
```

## Authentication note
The mobile wrapper uses the same staging Supabase email/password authentication as the staging website. Packaging the app does not bypass a wrong password, unconfirmed email, disabled account, or staging Auth configuration issue. If login still fails, capture the exact error shown in the app (never share a password) so the staging Auth issue can be diagnosed separately.
