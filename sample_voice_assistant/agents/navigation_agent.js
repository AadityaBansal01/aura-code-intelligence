/**
 * Navigation Agent
 * Handles geographic routes, turn-by-turn navigation, and location deeplinking.
 */

const permissionTool = require('../tools/permission_tool');
const deviceTool = require('../tools/device_tool');
const mapTool = require('../tools/map_tool');
const { DEEPLINKS } = require('../config/deeplinks');

class NavigationAgent {
    /**
     * Navigates user to designated frequent location (home / work)
     * Sequence: Requests ACCESS_FINE_LOCATION before launching navigation deeplink
     * @param {string} destinationType - 'home' | 'work'
     */
    async navigateToSavedLocation(destinationType) {
        console.log(`[NavigationAgent] Resolving route for destination: ${destinationType}`);

        // Step 1: Request GPS location permission before proceeding
        const permission = await permissionTool.requestPermissions('ACCESS_FINE_LOCATION');
        if (!permission.granted) {
            throw new Error('[NavigationAgent] Location access denied');
        }

        // Step 2: Determine appropriate navigation deeplink
        const deeplink = destinationType === 'work' 
            ? DEEPLINKS.NAVIGATION_NAVIGATE_WORK 
            : DEEPLINKS.NAVIGATION_NAVIGATE_HOME;

        // Step 3: Launch OS mapping navigation deeplink
        return await deviceTool.launchDeeplink(deeplink);
    }

    /**
     * Calculates on-screen turn-by-turn preview
     */
    async previewRoute(destinationAddress) {
        const hasPermission = await permissionTool.checkPermissions('ACCESS_FINE_LOCATION');
        if (!hasPermission) {
            await permissionTool.requestPermissions('ACCESS_FINE_LOCATION');
        }

        const geo = await mapTool.geocodeAddress(destinationAddress);
        return await mapTool.calculateRoute('CURRENT_LOCATION', `${geo.lat},${geo.lng}`);
    }
}

module.exports = new NavigationAgent();
