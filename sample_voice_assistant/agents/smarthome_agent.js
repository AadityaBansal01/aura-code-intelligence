/**
 * Smart Home Agent
 * Manages IoT appliances, Zigbee/Matter accessories, and cloud dispatch.
 */

const networkTool = require('../tools/network_tool');
const permissionTool = require('../tools/permission_tool');

class SmartHomeAgent {
    /**
     * Toggles smart lighting state across home hubs
     * Sequence: Verifies network connectivity before dispatching cloud payload
     * @param {string} roomName 
     * @param {boolean} turnOn 
     */
    async toggleLighting(roomName, turnOn) {
        console.log(`[SmartHomeAgent] Command received: ${roomName} lights -> ${turnOn ? 'ON' : 'OFF'}`);

        // Step 1: Check connectivity
        const network = await networkTool.checkConnectivity();
        if (!network.online) {
            throw new Error('[SmartHomeAgent] Cannot reach local SmartThings hub offline');
        }

        // Step 2: Dispatch endpoint payload
        const endpoint = `https://api.smartthings.com/v1/devices/${roomName}/commands`;
        return await networkTool.fetchEndpoint(endpoint, {
            method: 'POST',
            body: { command: turnOn ? 'switch.on' : 'switch.off' }
        });
    }

    /**
     * Sets target thermostat temperature
     */
    async setThermostat(room, degreesCelsius) {
        const net = await networkTool.checkConnectivity();
        if (!net.online) return { success: false, error: 'Hub offline' };

        return await networkTool.fetchEndpoint(`https://api.smartthings.com/v1/climate/${room}`, {
            method: 'PUT',
            body: { targetTemp: degreesCelsius }
        });
    }
}

module.exports = new SmartHomeAgent();
