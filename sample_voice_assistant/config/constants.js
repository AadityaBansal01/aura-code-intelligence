/**
 * Global Constants and Intent Enums for Voice Assistant Routing
 */

const INTENTS = {
    MEDIA_PLAY: 'media.playback.play',
    MEDIA_PAUSE: 'media.playback.pause',
    MEDIA_NEXT: 'media.playback.next',
    MEDIA_INTERRUPT: 'media.playback.interruption_ducking',
    
    BLUETOOTH_CONNECT: 'settings.bluetooth.connect',
    BLUETOOTH_OPEN_SETTINGS: 'settings.bluetooth.open',
    
    NAV_GET_DIRECTIONS: 'navigation.route.calculate',
    NAV_TRAFFIC_ALERT: 'navigation.traffic.report',
    
    SMARTHOME_LIGHTS_TOGGLE: 'smarthome.iot.lights_toggle',
    SMARTHOME_TEMPERATURE: 'smarthome.iot.climate_control',
    
    SYSTEM_DIAGNOSTICS: 'system.device.health_check',
    SYSTEM_BATTERY_OPTIMIZE: 'system.battery.optimize'
};

const TIMEOUTS = {
    VOICE_RECOGNITION_MS: 3500,
    TOOL_EXECUTION_MAX_MS: 5000,
    NETWORK_PING_MS: 1200
};

module.exports = { INTENTS, TIMEOUTS };
