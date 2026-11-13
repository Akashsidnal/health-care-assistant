# MediCare Cloud - Android Application & Mobile Access Guide

This folder contains the complete native Android project for **MediCare Cloud** (Smart Healthcare Monitoring & Medication Reminder System Using Cloud Technology).

---

## 2 Ways to Run on Mobile / Tablet

### Option 1: Instant Mobile PWA (Recommended for Tomorrow's Presentation — Zero Install Time)
The system is built as a **Progressive Web App (PWA)** with offline caching, push/alarm capabilities, and responsive UI:
1. Make sure your phone and laptop/PC are connected to the same Wi-Fi network.
2. Open **Chrome** (Android) or **Safari** (iOS) on your phone.
3. Type the LAN URL shown when running the server, e.g.:
   ```
   http://10.177.166.250:5000
   ```
4. On Chrome: Tap the 3-dot menu $\rightarrow$ **"Add to Home Screen"** or **"Install App"**.
5. The **MediCare Cloud** app icon will appear directly on your phone's home screen and launch full-screen just like an APK!
6. Audio alarms and reminders will chime live through the phone speakers.

---

### Option 2: Build Native APK in Android Studio
1. Open **Android Studio**.
2. Select **File $\rightarrow$ Open** and choose the directory:
   ```
   C:\Users\AKASH N SIDNAL\MediCareCloud\android\MediCareApp
   ```
3. Allow Gradle to sync dependencies.
4. If your laptop IP has changed from `10.177.166.250`, update the IP in `strings.xml` or enter it when prompted upon launching the app.
5. Click **Build $\rightarrow$ Build Bundle(s) / APK(s) $\rightarrow$ Build APK(s)**.
6. Transfer the generated `.apk` file to your Android phone via USB/WhatsApp/Drive and tap to install.
