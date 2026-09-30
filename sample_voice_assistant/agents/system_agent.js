/**
 * System Agent
 * Manages device health, battery profiles, and system diagnostics.
 */

const deviceTool = require('../tools/device_tool');
const { DEEPLINKS } = require('../config/deeplinks');

class SystemAgent {
    /**
     * Optimizes device battery by triggering low power mode and opening settings deeplink
     */
    async optimizeBatteryConsumption() {
        console.log('[SystemAgent] Analyzing device power profile');
        const status = await deviceTool.getBatteryStatus();

        if (status.level < 0.20) {
            console.log('[SystemAgent] Battery critical. Forwarding user to power management deeplink');
            return await deviceTool.launchDeeplink(DEEPLINKS.BATTERY_SAVER_SETTINGS);
        }

        // Adjust screen brightness to conservative level
        return await deviceTool.setBrightness(40);
    }

    /**
     * Opens system permission manager
     */
    async openPermissionManager() {
        return await deviceTool.launchDeeplink(DEEPLINKS.APP_PERMISSIONS_MANAGER);
    }
}

module.exports = new SystemAgent();
