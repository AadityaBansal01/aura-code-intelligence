/**
 * Voice Assistant Intent Dispatcher (Root Entrypoint)
 * Routes incoming voice queries, intent classifications, and speech sessions to specialized agents.
 */

const settingsAgent = require('./settings_agent');
const mediaAgent = require('./media_agent');
const navigationAgent = require('./navigation_agent');
const smartHomeAgent = require('./smarthome_agent');
const systemAgent = require('./system_agent');
const { INTENTS } = require('../config/constants');

class VoiceDispatcher {
    constructor() {
        this.activeSessions = new Map();
    }

    /**
     * Central dispatch router for all natural language voice commands
     * @param {string} intent - The classified intent name
     * @param {Object} payload - Extracted slot parameters
     */
    async dispatchVoiceIntent(intent, payload = {}) {
        console.log(`[VoiceDispatcher] Routing intent: ${intent}`);

        switch (intent) {
            case INTENTS.BLUETOOTH_OPEN_SETTINGS:
                return await settingsAgent.handleBluetoothSettingsRequest(payload);

            case INTENTS.BLUETOOTH_CONNECT:
                return await settingsAgent.pairBluetoothDevice(payload.deviceName || 'device');

            case INTENTS.MEDIA_INTERRUPT:
                return await mediaAgent.handlePlaybackInterruption(payload);

            case INTENTS.MEDIA_PLAY:
                return await mediaAgent.playTrack(payload.query || 'Favorites');

            case INTENTS.NAV_GET_DIRECTIONS:
                return await navigationAgent.navigateToSavedLocation(payload.destination || 'home');

            case INTENTS.SMARTHOME_LIGHTS_TOGGLE:
                return await smartHomeAgent.toggleLighting(payload.room || 'living_room', payload.state !== false);

            case INTENTS.SYSTEM_BATTERY_OPTIMIZE:
                return await systemAgent.optimizeBatteryConsumption();

            default:
                console.warn(`[VoiceDispatcher] Unhandled voice intent: ${intent}`);
                return { error: 'UNKNOWN_INTENT', intent };
        }
    }
}

module.exports = new VoiceDispatcher();
