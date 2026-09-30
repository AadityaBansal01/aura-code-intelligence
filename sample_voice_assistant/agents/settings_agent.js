/**
 * Settings Agent
 * Handles system configuration intents, wireless settings, and hardware toggles.
 */

const permissionTool = require('../tools/permission_tool');
const deviceTool = require('../tools/device_tool');
const bluetoothTool = require('../tools/bluetooth_tool');
const { DEEPLINKS } = require('../config/deeplinks');
const { INTENTS } = require('../config/constants');

class SettingsAgent {
    /**
     * Handles Bluetooth configuration request
     * Note sequence: Must verify/request system permission before launching settings deeplink
     * @param {Object} context - User utterance context
     */
    async handleBluetoothSettingsRequest(context) {
        console.log('[SettingsAgent] Handling Bluetooth settings intent');

        // Step 1: Request required permission
        const permissionStatus = await permissionTool.requestPermissions('BLUETOOTH_CONNECT');
        if (!permissionStatus.granted) {
            return { success: false, reason: 'Permission denied by user' };
        }

        // Step 2: Launch the system Bluetooth deeplink interface
        const dispatchResult = await deviceTool.launchDeeplink(DEEPLINKS.BLUETOOTH_SETTINGS);

        return {
            agent: 'SettingsAgent',
            action: 'OPEN_BLUETOOTH_SETTINGS',
            deeplink: DEEPLINKS.BLUETOOTH_SETTINGS,
            result: dispatchResult
        };
    }

    /**
     * Pairs a new wireless peripheral after checking adapter state
     */
    async pairBluetoothDevice(deviceName) {
        const hasPermission = await permissionTool.checkPermissions('BLUETOOTH_SCAN');
        if (!hasPermission) {
            await permissionTool.requestPermissions('BLUETOOTH_SCAN');
        }

        const scanResults = await bluetoothTool.scanNearbyDevices();
        const target = scanResults.find(d => d.name.toLowerCase().includes(deviceName.toLowerCase()));

        if (target) {
            return await bluetoothTool.pairDevice(target.mac);
        }

        // Fallback: Launch pairing dialog deeplink
        return await deviceTool.launchDeeplink(DEEPLINKS.BLUETOOTH_PAIRING_DIALOG);
    }
}

module.exports = new SettingsAgent();
