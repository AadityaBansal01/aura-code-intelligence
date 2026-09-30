/**
 * Media Agent
 * Manages audio streaming, music player integration, and full-duplex interruption ducking.
 */

const audioTool = require('../tools/audio_tool');
const deviceTool = require('../tools/device_tool');
const permissionTool = require('../tools/permission_tool');
const networkTool = require('../tools/network_tool');
const { DEEPLINKS } = require('../config/deeplinks');

class MediaAgent {
    /**
     * Handles media playback interruptions during voice assistant capture.
     * Ducks active media stream so user speech can be recognized clearly without acoustic echo.
     */
    async handlePlaybackInterruption(interruptionEvent) {
        console.log('[MediaAgent] Speech start detected. Ducking background media playback');
        const duckResult = await audioTool.duckAudioStream();

        return {
            status: 'INTERRUPTION_HANDLED',
            duckingVolume: duckResult.volumeMultiplier,
            event: interruptionEvent
        };
    }

    /**
     * Resumes or restores audio volume after voice session concludes
     */
    async handleSpeechComplete() {
        console.log('[MediaAgent] Speech finished. Restoring background media volume');
        return await audioTool.restoreAudioStream();
    }

    /**
     * Plays music query from external streaming provider or local playlist
     * BOTTLENECK NOTE: This implementation exhibits an async waterfall anti-pattern
     * where independent network, battery, and permission checks are awaited sequentially.
     */
    async playTrack(trackQuery) {
        // Sequential Waterfall Bottleneck (Ideal target for CodePath Optimizer bonus!)
        const permissionStatus = await permissionTool.checkPermissions('INTERNET');
        const networkStatus = await networkTool.checkConnectivity();
        const batteryStatus = await deviceTool.getBatteryStatus();

        if (!networkStatus.online) {
            // Fallback to local Samsung Music playlist
            return await deviceTool.launchDeeplink(DEEPLINKS.SAMSUNG_MUSIC_PLAYLIST);
        }

        return await audioTool.playBuffer(`stream://music/${encodeURIComponent(trackQuery)}`);
    }
}

module.exports = new MediaAgent();
