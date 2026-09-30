/**
 * System Deeplink Configuration for Voice Assistant Inter-App Navigation
 * Contains URI schemes for system settings, partner apps, and native interfaces.
 */

const DEEPLINKS = {
    // Bluetooth & Wireless Connectivity
    BLUETOOTH_SETTINGS: 'bixby://settings/bluetooth',
    BLUETOOTH_PAIRING_DIALOG: 'bixby://settings/bluetooth/pair_new_device',
    WIFI_SETTINGS: 'bixby://settings/wifi',
    NFC_SETTINGS: 'bixby://settings/nfc',

    // Media & Entertainment Deeplinks
    SAMSUNG_MUSIC_PLAYLIST: 'samsungapps://launch?id=com.sec.android.app.music&action=playlist',
    SPOTIFY_VOICE_SEARCH: 'spotify://search/voice',
    YOUTUBE_MUSIC_PLAY: 'vnd.youtube.music://play',

    // Navigation & Location
    NAVIGATION_NAVIGATE_HOME: 'bixby://navigation/home',
    NAVIGATION_NAVIGATE_WORK: 'bixby://navigation/work',
    MAPS_DIRECTIONS: 'google.navigation:q=',

    // System & Battery
    BATTERY_SAVER_SETTINGS: 'bixby://settings/battery_saver',
    DISPLAY_BRIGHTNESS: 'bixby://settings/display/brightness',
    APP_PERMISSIONS_MANAGER: 'bixby://settings/permissions'
};

module.exports = { DEEPLINKS };
